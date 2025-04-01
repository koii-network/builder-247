import { Request, Response } from "express";
import { IssueModel } from "../models/Issue";
import {
  getDistributionListSubmitter,
  getDistributionListWrapper,
  getKeysByValueSign,
} from "../taskOperations/getDistributionList";
import { IssueStatus } from "../models/Issue";
import { TodoModel, TodoStatus } from "../models/Todo";
// A simple in-memory cache to store processed task IDs and rounds
const cache: Record<string, Set<number>> = {};

export async function triggerFetchAuditResult(req: Request, res: Response): Promise<void> {
  const { taskId, round } = req.body;

  // Check if the taskId and round have already been processed
  if (cache[taskId] && cache[taskId].has(round)) {
    res.status(200).send("Task already processed.");
    return;
  }

  // If not processed, add to cache
  if (!cache[taskId]) {
    cache[taskId] = new Set();
  }
  cache[taskId].add(round);

  const submitter = await getDistributionListSubmitter(taskId, round);
  if (!submitter) {
    cache[taskId].delete(round);
    res.status(200).send("No Distribution List Submitter found.");
    return;
  }

  const distributionList = await getDistributionListWrapper("FttDHvbX3nM13TUrSvvS614Sgtr9418TC8NpvR7hkMcE", "361");

  let positiveKeys: string[] = [];
  let negativeKeys: string[] = [];
  if (distributionList) {
    const { positive, negative } = await getKeysByValueSign(distributionList);
    positiveKeys = positive;
    negativeKeys = negative;
  } else {
    cache[taskId].delete(round);
    res.status(200).send("No Distribution List found.");
    return;
  }

  const response = await triggerFetchAuditResultLogic(positiveKeys, negativeKeys, round);
  res.status(response.statuscode).json(response.data);
}

export const triggerFetchAuditResultLogic = async (positiveKeys: string[], negativeKeys: string[], round: number) => {
  // Update the subtask status
  const todos = await TodoModel.find({
    assignedStakingKey: { $in: [...positiveKeys, ...negativeKeys] },
    assignedRoundNumber: round,
  });

  for (const todo of todos) {
    if (positiveKeys.includes(todo.assignedStakingKey!)) {
      todo.status = TodoStatus.APPROVED;
    } else if (negativeKeys.includes(todo.assignedStakingKey!)) {
      todo.status = TodoStatus.INITIALIZED; // Reset status for negative audit
      todo.prUrl = undefined;
      todo.assignedStakingKey = undefined;
      todo.assignedGithubUsername = undefined;
      todo.assignedRoundNumber = undefined;
    }
    await todo.save();
  }

  // Get all the issue's for this round changed todos
  const issueUuids = todos.map((todo) => todo.issueUuid);

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
  const hasPRIssues = await IssueModel.find({
    assignedStakingKey: { $in: [...positiveKeys, ...negativeKeys] },
    prUrl: { $exists: true },
  });

  /// TODO: pretty sure this has a problem - we need to make sure the round number also matches
  for (const issue of hasPRIssues) {
    if (positiveKeys.includes(issue.assignedStakingKey!)) {
      issue.status = IssueStatus.IN_REVIEW;
      await TodoModel.updateMany({ issueUuid: issue.issueUuid }, { $set: { status: TodoStatus.MERGED } });
    }
    await issue.save();
  }

  return {
    statuscode: 200,
    data: {
      success: true,
      message: "Task processed successfully.",
    },
  };
};
