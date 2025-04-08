import { TodoModel, TodoStatus } from "../models/Todo";

export async function getPRDict(issueUuid: string) {
  const todos = await TodoModel.find({ issueUuid, status: TodoStatus.APPROVED })
    .select("prUrl assignedStakingKey")
    .lean();

  console.log("todos", todos);

  // Create a dictionary with staking keys as keys and arrays of PR URLs as values
  const prDict: Record<string, string[]> = {};

  // Add todos that have PR URLs and staking keys
  for (const todo of todos) {
    if (todo.prUrl && todo.assignedStakingKey) {
      if (!prDict[todo.assignedStakingKey]) {
        prDict[todo.assignedStakingKey] = [];
      }
      prDict[todo.assignedStakingKey].push(todo.prUrl);
    }
  }

  console.log("prDict", prDict);
  return prDict;
}
