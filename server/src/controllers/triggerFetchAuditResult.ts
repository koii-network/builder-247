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

export async function triggerFetchAuditResult(req: Request, res: Response): Promise<void> {
  const { taskId, round } = req.body;

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
    res.status(200).send(message);
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
    const submitter = await getDistributionListSubmitter(taskId, round);
    if (!submitter) {
      throw new Error("No Distribution List Submitter found");
    }

    const distributionList = await getDistributionListWrapper(submitter, round.toString());
    if (!distributionList) {
      throw new Error("No Distribution List found");
    }

    const { positive, negative } = await getKeysByValueSign(distributionList);
    await triggerFetchAuditResultLogic(positive, negative, round);

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

export const triggerFetchAuditResultLogic = async (positiveKeys: string[], negativeKeys: string[], round: number) => {
  const allKeys = [...positiveKeys, ...negativeKeys];

  // Update the subtask status
  const auditableTodos = await TodoModel.find({
    assignedStakingKey: { $in: allKeys },
    assignedRoundNumber: round,
    prUrl: { $exists: true },
  });

  for (const todo of auditableTodos) {
    if (positiveKeys.includes(todo.assignedStakingKey!)) {
      todo.status = TodoStatus.APPROVED;
    } else if (negativeKeys.includes(todo.assignedStakingKey!)) {
      todo.status = TodoStatus.INITIALIZED;
      todo.prUrl = undefined;
      todo.assignedStakingKey = undefined;
      todo.assignedGithubUsername = undefined;
      todo.assignedRoundNumber = undefined;
    }
    await todo.save();
  }

  // Get all the issue's for this round changed todos
  const issueUuids = auditableTodos.map((todo) => todo.issueUuid);

  // Check if all subtasks of an issue are completed
  const issues = await IssueModel.find({ issueUuid: { $in: issueUuids } });
  for (const issue of issues) {
    const todos = await TodoModel.find({ issueUuid: issue.issueUuid });
    if (todos.every((todo) => todo.status === TodoStatus.APPROVED)) {
      issue.status = IssueStatus.ASSIGN_PENDING;
    }
    await issue.save();
  }

  // Now update the has PR issues
  const auditableIssues = await IssueModel.find({
    assignedStakingKey: { $in: allKeys },
    assignedRoundNumber: round,
    prUrl: { $exists: true },
  });

  for (const issue of auditableIssues) {
    if (positiveKeys.includes(issue.assignedStakingKey!)) {
      issue.status = IssueStatus.IN_REVIEW;
      await TodoModel.updateMany({ issueUuid: issue.issueUuid }, { $set: { status: TodoStatus.MERGED } });
    }
    await issue.save();
  }
};
