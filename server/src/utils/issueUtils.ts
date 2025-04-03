import { IssueModel } from "../models/Issue";
import { TodoModel } from "../models/Todo";

export async function getPRDict(issueUuid: string) {
  const issue = await IssueModel.findOne({ issueUuid }).select("prUrl assignedStakingKey assignedRoundNumber").lean();

  if (!issue) {
    return null;
  }

  const todos = await TodoModel.find({ issueUuid }).select("prUrl assignedStakingKey assignedRoundNumber").lean();

  // Create a dictionary with staking keys as keys and PR URLs as values
  const prDict: Record<string, string> = {};

  // Add the main issue if it has a PR URL and staking key
  if (issue.prUrl && issue.assignedStakingKey) {
    prDict[issue.assignedStakingKey] = issue.prUrl;
  }

  // Add todos that have PR URLs and staking keys
  for (const todo of todos) {
    if (todo.prUrl && todo.assignedStakingKey) {
      prDict[todo.assignedStakingKey] = todo.prUrl;
    }
  }

  return prDict;
}
