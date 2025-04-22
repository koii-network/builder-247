import { TodoModel, TodoStatus } from "../models/Todo";

export async function getPRDict(issueUuid: string) {
  const todos = await TodoModel.find({ issueUuid, status: TodoStatus.APPROVED })
    .select("assignees")
    .lean();

  console.log("todos", todos);

  // Create a dictionary with staking keys as keys and arrays of PR URLs as values
  const prDict: Record<string, string[]> = {};

  // Add todos that have PR URLs and staking keys
  for (const todo of todos) {
    if (todo.assignees) {
      for (const assignee of todo.assignees) {
        if (assignee.prUrl && assignee.stakingKey) {
          if (!prDict[assignee.stakingKey]) {
            prDict[assignee.stakingKey] = [];
          }
          prDict[assignee.stakingKey].push(assignee.prUrl);
        }
      }
    }
  }

  console.log("prDict", prDict);
  return prDict;
}
