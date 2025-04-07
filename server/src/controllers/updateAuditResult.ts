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
  console.log(`[TEST MODE] Starting audit results processing for round ${round}`);

  // 1. Update IN_REVIEW todos to APPROVED if they have PR URLs
  const todosResult = await TodoModel.updateMany(
    {
      status: TodoStatus.IN_REVIEW,
      assignedRoundNumber: round,
      prUrl: { $exists: true, $ne: null },
    },
    {
      $set: { status: TodoStatus.APPROVED },
    },
  );

  console.log(`[TEST MODE] Updated ${todosResult.modifiedCount} todos from IN_REVIEW to APPROVED for round ${round}`);

  // 2. Find all IN_REVIEW issues (these are issues that have been audited by the leader)
  const inReviewIssues = await IssueModel.find({
    status: IssueStatus.IN_REVIEW,
    assignedRoundNumber: round,
    prUrl: { $exists: true, $ne: null },
  });

  console.log(`[TEST MODE] Found ${inReviewIssues.length} issues in IN_REVIEW status`);

  // 3. For each IN_REVIEW issue, check if all its todos are APPROVED and have PR URLs
  for (const issue of inReviewIssues) {
    console.log(`[TEST MODE] Processing issue ${issue.issueUuid}`);
    const todos = await TodoModel.find({ issueUuid: issue.issueUuid });
    console.log(`[TEST MODE] Found ${todos.length} todos for issue ${issue.issueUuid}`);

    const allTodosApprovedWithPRs =
      todos.length > 0 && todos.every((todo) => todo.status === TodoStatus.APPROVED && todo.prUrl);

    console.log(`[TEST MODE] All todos approved with PRs: ${allTodosApprovedWithPRs}`);
    console.log(
      `[TEST MODE] Todo statuses:`,
      todos.map((t) => ({
        id: t._id,
        status: t.status,
        hasPR: !!t.prUrl,
        assignedRoundNumber: t.assignedRoundNumber,
      })),
    );

    if (allTodosApprovedWithPRs) {
      // Update to APPROVED if all todos are approved and have PR URLs
      await IssueModel.updateOne({ _id: issue._id }, { $set: { status: IssueStatus.APPROVED } });
      console.log(`[TEST MODE] Updated issue ${issue.issueUuid} to APPROVED - all todos are approved with PR URLs`);
    } else {
      console.log(`[TEST MODE] Issue ${issue.issueUuid} remains IN_REVIEW - not all todos are approved with PR URLs`);
    }
  }

  // 4. For issues already in APPROVED, verify they should stay there
  const approvedIssues = await IssueModel.find({ status: IssueStatus.APPROVED });
  console.log(`[TEST MODE] Verifying ${approvedIssues.length} issues in APPROVED status`);

  for (const issue of approvedIssues) {
    console.log(`[TEST MODE] Verifying issue ${issue.issueUuid} in APPROVED status`);
    const todos = await TodoModel.find({ issueUuid: issue.issueUuid });
    console.log(`[TEST MODE] Found ${todos.length} todos for issue ${issue.issueUuid}`);

    const allTodosApprovedWithPRs =
      todos.length > 0 && todos.every((todo) => todo.status === TodoStatus.APPROVED && todo.prUrl);

    console.log(`[TEST MODE] All todos approved with PRs: ${allTodosApprovedWithPRs}`);
    console.log(
      `[TEST MODE] Todo statuses:`,
      todos.map((t) => ({
        id: t._id,
        status: t.status,
        hasPR: !!t.prUrl,
        assignedRoundNumber: t.assignedRoundNumber,
      })),
    );

    if (!allTodosApprovedWithPRs) {
      // If not all todos are approved with PR URLs, move back to IN_REVIEW
      await IssueModel.updateOne({ _id: issue._id }, { $set: { status: IssueStatus.IN_REVIEW } });
      console.log(
        `[TEST MODE] Moved issue ${issue.issueUuid} back to IN_REVIEW - not all todos are approved with PR URLs`,
      );
    }
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

  // Check if all subtasks of an issue are completed and have PR URLs
  const issues = await IssueModel.find({ issueUuid: { $in: issueUuids } });
  console.log(`Found ${issues.length} issues related to updated todos`);

  for (const issue of issues) {
    const todos = await TodoModel.find({ issueUuid: issue.issueUuid });
    if (todos.every((todo) => todo.status === TodoStatus.APPROVED && todo.prUrl)) {
      issue.status = IssueStatus.ASSIGN_PENDING;
      console.log(`Setting issue ${issue.issueUuid} to ASSIGN_PENDING - all todos approved with PR URLs`);
    } else {
      console.log(
        `Issue ${issue.issueUuid} remains in current status - not all todos are approved with PR URLs:`,
        todos.map((t) => ({ id: t._id, status: t.status, hasPR: !!t.prUrl })),
      );
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
