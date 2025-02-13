import { Request, Response } from "express";
import "dotenv/config";

import { TodoModel, TodoStatus } from "../models/Todo";
import { verifySignature } from "../utils/sign";
import { taskID } from "../constant";
import { isValidStakingKey } from "../utils/taskState";

// Verify the request body contains the right data
function verifyRequestBody(req: Request): { signature: string; pubKey: string; github_username: string } | null {
  try {
    const signature = req.body.signature as string;
    const pubKey = req.body.pubKey as string;
    const github_username = req.body.github_username as string;
    if (!signature || !pubKey || !github_username) {
      return null;
    }
    return { signature, pubKey, github_username };
  } catch {
    return null;
  }
}

// Confirm the signature is valid and contains the right data
async function verifySignatureData(signature: string, pubKey: string): Promise<{ roundNumber: number } | null> {
  try {
    const { data, error } = await verifySignature(signature, pubKey);
    if (error || !data) {
      console.log("bad signature");
      return null;
    }
    const body = JSON.parse(data);
    if (!body.taskId) console.log("no taskId");
    if (!body.roundNumber) console.log("no roundNumber");
    if (!body.action) console.log("no action");
    if (body.action !== "fetch") console.log("action is not fetch:", body.action);
    if (body.taskId !== taskID) console.log("taskId is not correct:", body.taskId, taskID);
    if (!body.taskId || !body.roundNumber || body.taskId !== taskID || body.action !== "fetch") {
      return null;
    }
    return { roundNumber: body.roundNumber };
  } catch (error) {
    console.log("unexpected signature error", error);
    return null;
  }
}

// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string, roundNumber: number) {
  try {
    const result = await TodoModel.findOne({
      "assignedTo.stakingKey": stakingKey,
      "assignedTo.roundNumber": roundNumber,
    })
      .select("assignedTo title acceptanceCriteria repoOwner repoName")
      .lean();

    if (!result) return null;

    // Find the specific assignment entry
    const assignment = result.assignedTo.find((a) => a.stakingKey === stakingKey && a.roundNumber === roundNumber);

    return {
      todo: result,
      hasPR: assignment?.prUrl ? true : false,
    };
  } catch (error) {
    console.error("Error checking assigned info:", error);
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

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.pubKey);
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  if (!(await isValidStakingKey(requestBody.pubKey))) {
    res.status(401).json({
      success: false,
      message: "Invalid staking key",
    });
    return;
  }
  console.log();
  const existingAssignment = await checkExistingAssignment(requestBody.pubKey, signatureData.roundNumber);

  if (existingAssignment) {
    if (existingAssignment.hasPR) {
      return res.status(401).json({
        success: false,
        message: "Task already completed",
      });
    } else {
      return res.status(200).json({
        success: true,
        data: {
          title: existingAssignment.todo.title,
          acceptance_criteria: existingAssignment.todo.acceptanceCriteria,
          repo_owner: existingAssignment.todo.repoOwner,
          repo_name: existingAssignment.todo.repoName,
          system_prompt: process.env.SYSTEM_PROMPT,
        },
      });
    }
  }

  try {
    const todos = await TodoModel.find({
      status: TodoStatus.INITIALIZED,
      $expr: { $lt: [{ $size: "$assignedTo" }, 2] },
      $nor: [
        { "assignedTo.stakingKey": requestBody.pubKey },
        { "assignedTo.githubUsername": requestBody.github_username },
      ],
    }).sort({ createdAt: 1 });

    if (todos.length === 0) {
      res.status(404).json({
        success: false,
        message: "No todos available",
      });
      return;
    }
    console.log(
      "todos listed",
      todos.map((todo) => todo.title),
    );

    const updatedTodo = await TodoModel.findOneAndUpdate(
      {
        _id: todos[0]?._id,
        $expr: { $lt: [{ $size: "$assignedTo" }, 5] },
        $nor: [
          { "assignedTo.stakingKey": requestBody.pubKey },
          { "assignedTo.githubUsername": requestBody.github_username },
        ],
      },
      {
        $push: {
          assignedTo: {
            stakingKey: requestBody.pubKey,
            taskId: taskID,
            roundNumber: signatureData.roundNumber,
            githubUsername: requestBody.github_username,
          },
        },
      },
      { new: true },
    );

    if (!updatedTodo) {
      res.status(409).json({
        success: false,
        message: "Task assignment conflict",
      });
      return;
    }

    res.status(200).json({
      success: true,
      data: {
        title: updatedTodo.title,
        acceptance_criteria: updatedTodo.acceptanceCriteria,
        repo_owner: updatedTodo.repoOwner,
        repo_name: updatedTodo.repoName,
        system_prompt: process.env.SYSTEM_PROMPT,
      },
    });
  } catch (error) {
    console.error("Error fetching todos:", error);
    res.status(500).json({
      success: false,
      message: "Failed to fetch todos",
    });
  }
};
