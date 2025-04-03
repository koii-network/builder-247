import { Request, Response } from "express";
import { IssueModel } from "../models/Issue";
import {
  getDistributionListSubmitter,
  getDistributionListWrapper,
  getKeysByValueSign,
} from "../taskOperations/getDistributionList";
import { IssueStatus } from "../models/Issue";
import { TodoModel, TodoStatus } from "../models/Todo";
import { AuditModel, AuditStatus } from "../models/Audit";

const PROCESS_TIMEOUT = 10 * 60 * 1000; // 10 minutes
const BYPASS_TASK_STATE_CHECK = process.env.BYPASS_TASK_STATE_CHECK === "true";

/**
 * Verify the request body for update-audit-result endpoint
 */
function verifyRequestBody(req: Request): { taskId: string; round: number } | null {
  console.log("updateAuditResult request body:", req.body);
  try {
    const taskId = req.body.taskId as string;
    const round = req.body.round as number;

    if (!taskId || typeof round !== "number") {
      return null;
    }

    return { taskId, round };
  } catch {
    return null;
  }
}

export async function updateAuditResult(req: Request, res: Response): Promise<void> {
  // Verify the request body
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(400).json({
      success: false,
      message: "Invalid request body. Required fields: taskId (string), round (number)",
    });
    return;
  }

  const { taskId, round } = requestBody;

  // Check for existing audit
  const existingAudit = await AuditModel.findOne({
    taskId: taskId,
    roundNumber: round,
    $or: [
      { status: AuditStatus.COMPLETED },
      {
        status: AuditStatus.IN_PROGRESS,
        updatedAt: { $gt: new Date(Date.now() - PROCESS_TIMEOUT) },
      },
    ],
  });

  if (existingAudit) {
    const message =
      existingAudit.status === AuditStatus.COMPLETED ? "Task already processed." : "Task is being processed.";
    res.status(200).json({
      success: true,
      message,
    });
    return;
  }

  // Case 3: Stale or failed - retry processing
  const audit = await AuditModel.findOneAndUpdate(
    {
      taskId: taskId,
      roundNumber: round,
    },
    {
      status: AuditStatus.IN_PROGRESS,
      error: null,
    },
    { upsert: true, new: true },
  );

  try {
    // Check if this is a test environment
    if (BYPASS_TASK_STATE_CHECK) {
      console.log(`[TEST MODE] Update audit result in test mode for round ${round}`);

      // In test mode, directly update todos and issues without checking distribution list
      await updateTestEnvironmentStatus(round);

      await AuditModel.findByIdAndUpdate(audit._id, {
        status: AuditStatus.COMPLETED,
      });

      res.status(200).json({
        success: true,
        message: "[TEST MODE] Task processed successfully.",
      });
      return;
    }

    // Normal production flow - use distribution list
    let positiveKeys: string[] = [];
    let negativeKeys: string[] = [];

    const submitter = await getDistributionListSubmitter(taskId, String(round));
    if (!submitter) {
      throw new Error("No Distribution List Submitter found");
    }

    const distributionList = await getDistributionListWrapper(taskId, String(round));
    if (!distributionList) {
      throw new Error("No Distribution List found");
    }

    const { positive, negative } = await getKeysByValueSign(distributionList);
    positiveKeys = positive;
    negativeKeys = negative;

    await triggerFetchAuditResultLogic(positiveKeys, negativeKeys, round);

    await AuditModel.findByIdAndUpdate(audit._id, {
      status: AuditStatus.COMPLETED,
    });

    res.status(200).json({
      success: true,
      message: "Task processed successfully.",
    });
  } catch (error) {
    await AuditModel.findByIdAndUpdate(audit._id, {
      status: AuditStatus.FAILED,
      error: error instanceof Error ? error.message : "Unknown error",
    });
    res.status(500).json({
      success: false,
      message: "Audit processing failed",
      error: error instanceof Error ? error.message : error,
    });
  }
}

/**
 * Special function for test environment to update todos and issues statuses
 * without needing to check the distribution list
 */
async function updateTestEnvironmentStatus(round: number): Promise<void> {
  // 1. Update all IN_PROGRESS todos to APPROVED
  const todosResult = await TodoModel.updateMany(
    {
      status: TodoStatus.IN_REVIEW,
      assignedRoundNumber: round,
    },
    {
      $set: { status: TodoStatus.APPROVED },
    },
  );

  console.log(`[TEST MODE] Updated ${todosResult.modifiedCount} todos from IN_PROGRESS to APPROVED for round ${round}`);

  // 2. Update all IN_PROGRESS issues to ASSIGN_PENDING
  const issuesResult = await IssueModel.updateMany(
    {
      status: IssueStatus.IN_PROGRESS,
    },
    {
      $set: { status: IssueStatus.ASSIGN_PENDING },
    },
  );

  console.log(`[TEST MODE] Updated ${issuesResult.modifiedCount} issues from IN_PROGRESS to ASSIGN_PENDING`);

  // 3. Keep ASSIGN_PENDING issues as ASSIGN_PENDING for leader tasks
  // (No need to change status here, they're already in the correct state)
  const pendingIssuesCount = await IssueModel.countDocuments({ status: IssueStatus.ASSIGN_PENDING });
  console.log(`[TEST MODE] Found ${pendingIssuesCount} issues already in ASSIGN_PENDING status`);

  // 4. Ensure that todos for issues in ASSIGN_PENDING status are properly marked
  const pendingIssues = await IssueModel.find({ status: IssueStatus.ASSIGN_PENDING });
  console.log(`[TEST MODE] Processing ${pendingIssues.length} issues in ASSIGN_PENDING status`);

  for (const issue of pendingIssues) {
    // Update todos for this issue
    const todosForIssueResult = await TodoModel.updateMany(
      { issueUuid: issue.issueUuid },
      { $set: { status: TodoStatus.APPROVED } },
    );

    console.log(`[TEST MODE] Updated ${todosForIssueResult.modifiedCount} todos for issue ${issue.issueUuid}`);
  }
}

export const triggerFetchAuditResultLogic = async (positiveKeys: string[], negativeKeys: string[], round: number) => {
  const allKeys = [...positiveKeys, ...negativeKeys];

  console.log(`Processing audit results for round ${round}`);
  console.log(`Positive keys: ${positiveKeys.length}, Negative keys: ${negativeKeys.length}`);

  // Update the subtask status
  const auditableTodos = await TodoModel.find({
    assignedStakingKey: { $in: allKeys },
    assignedRoundNumber: round,
    prUrl: { $exists: true },
  });

  console.log(`Found ${auditableTodos.length} auditable todos`);

  for (const todo of auditableTodos) {
    if (positiveKeys.includes(todo.assignedStakingKey!)) {
      todo.status = TodoStatus.APPROVED;
      console.log(`Approving todo ${todo._id} with key ${todo.assignedStakingKey}`);
    } else if (negativeKeys.includes(todo.assignedStakingKey!)) {
      todo.status = TodoStatus.INITIALIZED;
      todo.prUrl = undefined;
      todo.assignedStakingKey = undefined;
      todo.assignedGithubUsername = undefined;
      todo.assignedRoundNumber = undefined;
      console.log(`Rejecting todo ${todo._id}`);
    }
    await todo.save();
  }

  // Get all the issue's for this round changed todos
  const issueUuids = auditableTodos.map((todo) => todo.issueUuid);

  // Check if all subtasks of an issue are completed
  const issues = await IssueModel.find({ issueUuid: { $in: issueUuids } });
  console.log(`Found ${issues.length} issues related to updated todos`);

  for (const issue of issues) {
    const todos = await TodoModel.find({ issueUuid: issue.issueUuid });
    if (todos.every((todo) => todo.status === TodoStatus.APPROVED)) {
      issue.status = IssueStatus.ASSIGN_PENDING;
      console.log(`Setting issue ${issue.issueUuid} to ASSIGN_PENDING`);
    }
    await issue.save();
  }

  // Now update the has PR issues
  const auditableIssues = await IssueModel.find({
    assignedStakingKey: { $in: allKeys },
    assignedRoundNumber: round,
    prUrl: { $exists: true },
  });

  console.log(`Found ${auditableIssues.length} auditable issues`);

  for (const issue of auditableIssues) {
    if (positiveKeys.includes(issue.assignedStakingKey!)) {
      issue.status = IssueStatus.ASSIGN_PENDING;
      console.log(`Setting issue ${issue.issueUuid} to ASSIGN_PENDING`);
      await TodoModel.updateMany({ issueUuid: issue.issueUuid }, { $set: { status: TodoStatus.MERGED } });
    }
    await issue.save();
  }
};
