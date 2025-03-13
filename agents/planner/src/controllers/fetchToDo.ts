import { Request, Response } from "express";
import "dotenv/config";

import { TodoModel, TodoStatus } from "../models/Todo";
import { verifySignature } from "../utils/sign";
import { taskID } from "../constant";
import { isValidStakingKey } from "../utils/taskState";
import { IssueModel, IssueStatus } from "../models/Issue";
// Verify the request body contains the right data
function verifyRequestBody(req: Request): { signature: string; stakingKey: string; pubKey: string } | null {
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

// Confirm the signature is valid and contains the right data
async function verifySignatureData(
  signature: string,
  stakingKey: string,
  pubKey: string,
): Promise<{ roundNumber: number; githubUsername: string } | null> {
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
      body.taskId !== taskID ||
      body.action !== "fetch" ||
      !body.githubUsername ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      console.log("bad signature data");
      return null;
    }
    return { roundNumber: body.roundNumber, githubUsername: body.githubUsername };
  } catch (error) {
    console.log("unexpected signature error", error);
    return null;
  }
}

// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string, roundNumber: number) {
  try {
    const result = await TodoModel.findOne({
      assignedTo: {
        $elemMatch: {
          taskId: taskID,
          stakingKey: stakingKey,
          roundNumber: roundNumber,
        },
      },
    })
      .select("assignedTo title acceptanceCriteria repoOwner repoName")
      .lean();

    if (!result) return null;

    // Find the specific assignment entry
    const assignment = result.assignedTo.find(
      (a: any) => a.stakingKey === stakingKey && a.roundNumber === roundNumber && a.taskId === taskID,
    );

    return {
      todo: result,
      hasPR: Boolean(assignment?.prUrl),
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

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.stakingKey, requestBody.pubKey);
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  if (!(await isValidStakingKey(requestBody.stakingKey))) {
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
    // TODO: We must consider concurrent requests
    const todos = await TodoModel.find({
      // Not assigned to the current user
      
      $nor: [
        { "assignedTo.stakingKey": requestBody.pubKey },
        { "assignedTo.githubUsername": signatureData.githubUsername },
      ],
      $or: [
        { $and: [{ "assignedTo.roundNumber": { $lt: signatureData.roundNumber - 4} }, { status: TodoStatus.IN_PROGRESS }] },
        { $and: [{ status: TodoStatus.INITIALIZED }] }
      ], 
      
    }).sort({ createdAt: 1 });


    const dependencyFinishedTodosUUID = [];

    for (const todo of todos) {
      let isDependencyFinished = true;
      for (const dependency of todo.dependencyTasks) {
        const dependencyFinishedTodo = await TodoModel.findOne({
          _id: dependency,
          status: TodoStatus.AUDITED,
        });
        if (!dependencyFinishedTodo) {
          isDependencyFinished = false;
          break;
        }
      }
      if (isDependencyFinished) {
        dependencyFinishedTodosUUID.push(todo._id);
      }
    }

    if (todos.length === 0 || dependencyFinishedTodosUUID.length === 0) {
      res.status(404).json({
        success: false,
        message: `No todos available, todos: ${todos.length}, dependencyFinishedTodosUUID: ${dependencyFinishedTodosUUID.length}`,
      });
      return;
    }
    console.log("todos listed:", todos.length);
    // Explain: The reason why I find again is to make it modular
    const updatedTodo = await TodoModel.findOneAndUpdate({
      // Not assigned to the current user
      
        $nor: [
          { "assignedTo.stakingKey": requestBody.pubKey },
          { "assignedTo.githubUsername": signatureData.githubUsername },
        ],
        $or: [
          { $and: [{ "assignedTo.roundNumber": { $lt: signatureData.roundNumber - 3 } }, { status: TodoStatus.IN_PROGRESS }] },
          { $and: [ { status: TodoStatus.INITIALIZED }] }
        ], 
        _id: { $in: dependencyFinishedTodosUUID },
    }, 
    {
      $push: {
        assignedTo: {
          stakingKey: requestBody.stakingKey,
          pubkey: requestBody.pubKey,
          taskId: taskID,
          roundNumber: signatureData.roundNumber,
          githubUsername: signatureData.githubUsername,
          todoSignature: requestBody.signature,
        },
      },
      status: TodoStatus.IN_PROGRESS,
    },
    { new: true },
  ).sort({ createdAt: 1 });

    if (!updatedTodo) {
      res.status(409).json({
        success: false,
        message: "Task assignment conflict",
      });
      return;
    }
    // Dependency Task PR URLs
    const dependencyTaskPRUrls = [];
    for (const dependency of updatedTodo.dependencyTasks) {
      const dependencyTask = await TodoModel.findOne({
        _id: dependency,
      });
      
      const firstValidAssignment = dependencyTask?.assignedTo.find((assignment: any) => assignment.prUrl);
      dependencyTaskPRUrls.push(firstValidAssignment?.prUrl);
    }
    // Elect Leader/Aggregator Node Part
    // Check all issues if there is any issue in ASSIGN_PENDING status, if there is, return the issue uuid
    const issue = await IssueModel.findOne({
      status: IssueStatus.ASSIGN_PENDING,
    });
    let electLeader = false;
    let issueUuid = "";
    if (issue){
      issueUuid = issue.issueUuid;
      electLeader = true;
    }
    // Elect Leader/Aggregator Node Part
    
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
