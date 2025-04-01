import { IssueModel } from "../models/Issue";
import { TodoModel } from "../models/Todo";

export async function getPRDict(issueUuid: string) {
  const issue = await IssueModel.findOne({ issueUuid }).select("prUrl assignedStakingKey assignedRoundNumber").lean();

  if (!issue) {
    return null;
  }

  const todos = await TodoModel.find({ issueUuid }).select("prUrl assignedStakingKey assignedRoundNumber").lean();

  const prDict = {
    issue: {
      prUrl: issue.prUrl,
      stakingKey: issue.assignedStakingKey,
      roundNumber: issue.assignedRoundNumber,
    },
    todos: todos.map((todo) => ({
      prUrl: todo.prUrl,
      stakingKey: todo.assignedStakingKey,
      roundNumber: todo.assignedRoundNumber,
    })),
  };

  return prDict;
}
