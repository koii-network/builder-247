import { Request, Response } from "express";
import "dotenv/config";

import { TodoModel, TodoStatus } from "../models/Todo";
import { taskIDs } from "../constant";
import { isValidStakingKey } from "../utils/taskState";
import { IssueModel, IssueStatus } from "../models/Issue";
import { verifySignature } from "../utils/sign";
import { SystemPromptModel } from "../models/SystemPrompt";

// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string, roundNumber: number, taskId: string) {
  try {
    const result = await TodoModel.findOne({
      assignedStakingKey: stakingKey,
      assignedRoundNumber: roundNumber,
      taskId: taskId,
    })
      .select("title acceptanceCriteria repoOwner repoName issueUuid prUrl")
      .lean();

    if (!result) return null;

    return {
      todo: result,
      hasPR: Boolean(result.prUrl),
    };
  } catch (error) {
    console.error("Error checking assigned info:", error);
    return null;
  }
}
export function verifyRequestBody(req: Request): { signature: string; stakingKey: string; pubKey: string } | null {
  console.log("verifyRequestBody", req.body);
  try {
    const signature = req.body.signature as string;
    const stakingKey = req.body.stakingKey as string;
    const pubKey = req.body.pubKey as string;
    if (!signature || !stakingKey || !pubKey) {
      return null;
    }
    return { signature, stakingKey, pubKey };
  } catch {
    return null;
  }
}
async function verifySignatureData(
  signature: string,
  stakingKey: string,
  pubKey: string,
  action: string,
): Promise<{ roundNumber: number; githubUsername: string; taskId: string } | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log("bad signature");
      return null;
    }
    const body = JSON.parse(data);
    console.log({ signature_payload: body });
    if (
      !body.taskId ||
      typeof body.roundNumber !== "number" ||
      !taskIDs.includes(body.taskId) ||
      body.action !== action ||
      !body.githubUsername ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      console.log("bad signature data");
      return null;
    }
    return { roundNumber: body.roundNumber, githubUsername: body.githubUsername, taskId: body.taskId };
  } catch (error) {
    console.log("unexpected signature error", error);
    return null;
  }
}

export const fetchTodo = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(
    requestBody.signature,
    requestBody.stakingKey,
    requestBody.pubKey,
    "fetch-todo",
  );
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  if (!(await isValidStakingKey(requestBody.stakingKey, signatureData.taskId))) {
    res.status(401).json({
      success: false,
      message: "Invalid staking key",
    });
    return;
  }
  const response = await fetchTodoLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);
};

export const fetchTodoLogic = async (
  requestBody: { signature: string; stakingKey: string; pubKey: string },
  signatureData: { roundNumber: number; githubUsername: string; taskId: string },
) => {
  // 1. Check if user already has an assignment
  const existingAssignment = await checkExistingAssignment(
    requestBody.stakingKey,
    signatureData.roundNumber,
    signatureData.taskId,
  );
  if (existingAssignment) {
    if (existingAssignment.hasPR) {
      return {
        statuscode: 401,
        data: {
          success: false,
          message: "Task already completed",
        },
      };
    }
    return {
      statuscode: 200,
      data: {
        success: true,
        data: {
          title: existingAssignment.todo.title,
          issueUuid: existingAssignment.todo.issueUuid,
          acceptance_criteria: existingAssignment.todo.acceptanceCriteria,
          repo_owner: existingAssignment.todo.repoOwner,
          repo_name: existingAssignment.todo.repoName,
        },
      },
    };
  }

  try {
    // 1. Find the current in-process issue
    const currentIssue = await IssueModel.findOne({
      status: IssueStatus.IN_PROCESS,
    });

    if (!currentIssue) {
      return {
        statuscode: 404,
        data: {
          success: false,
          message: "No active issue found",
        },
      };
    }

    // Make sure we have aggregator info
    if (!currentIssue.aggregatorOwner || !currentIssue.aggregatorUrl) {
      return {
        statuscode: 400,
        data: {
          success: false,
          message: "No aggregator info found for the active issue",
        },
      };
    }

    // 2. Use aggregation to find eligible todos
    const eligibleTodos = await TodoModel.aggregate([
      // Match initial criteria
      {
        $match: {
          issueUuid: currentIssue.issueUuid,
          $nor: [
            { assignedStakingKey: requestBody.stakingKey },
            { assignedGithubUsername: signatureData.githubUsername },
          ],
          $or: [
            { status: TodoStatus.INITIALIZED },
            {
              $and: [
                { status: TodoStatus.IN_PROGRESS },
                { assignedRoundNumber: { $lt: signatureData.roundNumber - 4 } },
              ],
            },
          ],
        },
      },
      // Lookup dependencies
      {
        $lookup: {
          from: "todos", // assuming collection name is "todos"
          let: { dependencyTasks: { $ifNull: ["$dependencyTasks", []] } },
          pipeline: [
            {
              $match: {
                $expr: {
                  $and: [{ $in: ["$uuid", "$$dependencyTasks"] }, { $ne: ["$status", TodoStatus.APPROVED] }],
                },
              },
            },
          ],
          as: "unmetDependencies",
        },
      },
      // Only keep todos with no unmet dependencies
      {
        $match: {
          $or: [
            { dependencyTasks: { $size: 0 } }, // no dependencies
            { unmetDependencies: { $size: 0 } }, // all dependencies met
          ],
        },
      },
      // Sort by creation date
      {
        $sort: { createdAt: 1 },
      },
      // Take the first one
      {
        $limit: 1,
      },
    ]);

    if (eligibleTodos.length === 0) {
      return {
        statuscode: 409,
        data: {
          success: false,
          message: "No todos with completed dependencies available",
        },
      };
    }

    // 3. Assign the eligible todo to the worker
    const updatedTodo = await TodoModel.findOneAndUpdate(
      { _id: eligibleTodos[0]._id, status: TodoStatus.INITIALIZED },
      {
        assignedStakingKey: requestBody.stakingKey,
        assignedGithubUsername: signatureData.githubUsername,
        assignedRoundNumber: signatureData.roundNumber,
        status: TodoStatus.IN_PROGRESS,
      },
      { new: true },
    );

    if (!updatedTodo) {
      return {
        statuscode: 409,
        data: {
          success: false,
          message: "Task assignment conflict",
        },
      };
    }

    // Get task-specific system prompt
    const systemPrompt = await SystemPromptModel.findOne({ taskId: signatureData.taskId });
    if (!systemPrompt) {
      return {
        statuscode: 500,
        data: {
          success: false,
          message: "System prompt not found for task",
        },
      };
    }

    return {
      statuscode: 200,
      data: {
        success: true,
        data: {
          title: updatedTodo.title,
          issue_uuid: updatedTodo.issueUuid,
          acceptance_criteria: updatedTodo.acceptanceCriteria,
          repo_owner: currentIssue.aggregatorOwner,
          repo_name: updatedTodo.repoName,
          aggregator_url: currentIssue.aggregatorUrl,
          system_prompt: systemPrompt.prompt,
        },
      },
    };
  } catch (error) {
    console.error("Error fetching todo:", error);
    return {
      statuscode: 500,
      data: {
        success: false,
        message: "Failed to fetch todo",
      },
    };
  }
};
