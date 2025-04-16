import { Request, Response } from "express";
import { IssueModel } from "../../models/Issue";
import {
  getDistributionListSubmitter,
  getDistributionListWrapper,
  getKeysByValueSign,
} from "../../utils/taskState/getDistributionList";
import { IssueStatus } from "../../models/Issue";
import { TodoModel, TodoStatus } from "../../models/Todo";
import { AuditModel, AuditStatus } from "../../models/Audit";

const PROCESS_TIMEOUT = 10 * 60 * 1000; // 10 minutes
const BYPASS_TASK_STATE_CHECK = process.env.NODE_ENV === "development";

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

  if (BYPASS_TASK_STATE_CHECK) {
    console.log(`[TEST MODE] Update audit result in test mode for round ${round}`);

    // In test mode, directly update todos and issues without checking distribution list
    await updateTestEnvironmentStatus(round);
    res.status(200).json({
      success: true,
      message: "[TEST MODE] Task processed successfully.",
    });
    return;
  }

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
    // Normal production flow - use distribution list
    let positiveKeys: string[] = [];
    let negativeKeys: string[] = [];

    const submitter = await getDistributionListSubmitter(taskId, String(round));
    if (!submitter) {
      await TodoModel.updateMany(
        { assignedRoundNumber: round },
        {
          $set: {
            status: TodoStatus.INITIALIZED,
            assignedStakingKey: undefined,
            assignedGithubUsername: undefined,
            assignedRoundNumber: undefined,
          },
        },
      );
      throw new Error("No Distribution List Submitter found");
    }

    const distributionList = await getDistributionListWrapper(taskId, String(round));
    if (!distributionList) {
      await TodoModel.updateMany(
        { assignedRoundNumber: round },
        {
          $set: {
            status: TodoStatus.INITIALIZED,
            assignedStakingKey: undefined,
            assignedGithubUsername: undefined,
            assignedRoundNumber: undefined,
          },
        },
      );
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
  const inReviewTodos = await TodoModel.find({
    status: TodoStatus.IN_REVIEW,
    "assignees.roundNumber": round,
    "assignees.prUrl": { $exists: true, $ne: null },
  });

  for (const todo of inReviewTodos) {
    todo.status = TodoStatus.APPROVED;
    const assignee = todo.assignees?.find((a) => a.roundNumber === round);
    if (assignee) {
      assignee.approved = true;
    }
    await todo.save();
  }

  console.log(`[TEST MODE] Updated ${inReviewTodos.length} todos from IN_REVIEW to APPROVED for round ${round}`);

  // 2. Find all IN_PROGRESS issues (these are issues that have been audited by the leader)
  const inProgressIssues = await IssueModel.find({ status: IssueStatus.IN_PROGRESS });

  console.log(`[TEST MODE] Found ${inProgressIssues.length} issues in IN_PROGRESS status`);

  // 3. For each IN_PROGRESS issue, check if all its todos are APPROVED
  for (const issue of inProgressIssues) {
    console.log(`[TEST MODE] Processing issue ${issue.issueUuid}`);
    const todos = await TodoModel.find({ issueUuid: issue.issueUuid });
    console.log(`[TEST MODE] Found ${todos.length} todos for issue ${issue.issueUuid}`);

    const allTodosApproved = todos.every((todo) => todo.status === TodoStatus.APPROVED);

    console.log(`[TEST MODE] All todos approved: ${allTodosApproved}`);

    if (allTodosApproved) {
      // Update to ASSIGN_PENDING if all todos are approved
      await IssueModel.updateOne({ _id: issue._id }, { $set: { status: IssueStatus.ASSIGN_PENDING } });
      console.log(`[TEST MODE] Updated issue ${issue.issueUuid} to ASSIGN_PENDING - all todos are approved`);
    } else {
      console.log(`[TEST MODE] Issue ${issue.issueUuid} remains IN_PROGRESS - not all todos are approved`);
    }
  }

  // 4. For issues IN_REVIEW, update them to APPROVED and set assignee.approved
  const inReviewIssues = await IssueModel.find({ status: IssueStatus.IN_REVIEW });
  for (const issue of inReviewIssues) {
    issue.status = IssueStatus.APPROVED;
    const assignee = issue.assignees?.find((a) => a.roundNumber === round);
    if (assignee) {
      assignee.approved = true;
    }
    await issue.save();
  }
  console.log(`[TEST MODE] Updated ${inReviewIssues.length} issues from IN_REVIEW to APPROVED`);
}

export const triggerFetchAuditResultLogic = async (positiveKeys: string[], negativeKeys: string[], round: number) => {
  console.log(`Processing audit results for round ${round}`);
  console.log(`Positive keys: ${positiveKeys.length}, Negative keys: ${negativeKeys.length}`);

  // Update the subtask status
  const auditableTodos = await TodoModel.find({ "assignees.roundNumber": round });

  console.log(`Found ${auditableTodos.length} auditable todos`);

  for (const todo of auditableTodos) {
    const assignee = todo.assignees?.find((a) => a.roundNumber === round);
    if (!assignee) continue;

    if (positiveKeys.includes(assignee.stakingKey)) {
      todo.status = TodoStatus.APPROVED;
      assignee.approved = true;
      console.log(`Approving todo ${todo._id} with key ${assignee.stakingKey}`);
    } else {
      todo.status = TodoStatus.INITIALIZED;
      assignee.prUrl = undefined;
      assignee.approved = false;
      console.log(`Rejecting todo ${todo._id}`);
    }
    await todo.save();
  }

  // Check all in progress issues
  const issues = await IssueModel.find({ status: IssueStatus.IN_PROGRESS });
  console.log(`Found ${issues.length} issues related to updated todos`);

  for (const issue of issues) {
    const todos = await TodoModel.find({ issueUuid: issue.issueUuid });
    if (todos.every((todo) => todo.status === TodoStatus.APPROVED)) {
      issue.status = IssueStatus.ASSIGN_PENDING;
      console.log(`Setting issue ${issue.issueUuid} to ASSIGN_PENDING - all todos approved`);
    } else {
      console.log(
        `Issue ${issue.issueUuid} remains in current status - not all todos are approved:`,
        todos.map((t) => ({
          id: t._id,
          status: t.status,
        })),
      );
    }
    await issue.save();
  }

  // Now update the has PR issues
  const auditedIssues = await IssueModel.find({ "assignees.roundNumber": round });

  console.log(`Found ${auditedIssues.length} audited issues`);

  for (const issue of auditedIssues) {
    const assignee = issue.assignees?.find((a) => a.roundNumber === round);
    if (!assignee) continue;

    if (positiveKeys.includes(assignee.stakingKey)) {
      issue.status = IssueStatus.APPROVED;
      assignee.approved = true;
      await issue.save();
      console.log(`Setting issue ${issue.issueUuid} to APPROVED`);
      await TodoModel.updateMany({ issueUuid: issue.issueUuid }, { $set: { status: TodoStatus.MERGED } });
    } else {
      issue.status = IssueStatus.ASSIGN_PENDING;
      assignee.approved = false;
      await issue.save();
      console.log(`Setting issue back to ${issue.issueUuid} to ASSIGN_PENDING`);
    }
  }
};
