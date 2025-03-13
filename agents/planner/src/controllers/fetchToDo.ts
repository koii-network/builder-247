import { Request, Response } from "express";
import "dotenv/config";

import { TodoModel, TodoStatus } from "../models/Todo";
import { taskID } from "../constant";
import { isValidStakingKey } from "../utils/taskState";
import { IssueModel, IssueStatus } from "../models/Issue";
import { verifySignature } from "../utils/sign";



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
    return { roundNumber: body.roundNumber, githubUsername: body.githubUsername };
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

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.stakingKey, requestBody.pubKey, "fetch");
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

      const chosenTODOIssue = await IssueModel.findOne({
        issueUuid: existingAssignment.todo.issueUuid,
      });

      const aggregatorInfo = chosenTODOIssue?.aggregator;

      return res.status(200).json({
        success: true,
        role: "worker",
        data: {
          title: existingAssignment.todo.title,
          acceptance_criteria: existingAssignment.todo.acceptanceCriteria,
          repo_owner: existingAssignment.todo.repoOwner,
          repo_name: existingAssignment.todo.repoName,
          system_prompt: process.env.SYSTEM_PROMPT,
          aggregator_info: aggregatorInfo,
        },
      });
    }
  }
  // Check if there are not assigned issues
  const notAssignedIssue = await IssueModel.findOneAndUpdate({
    status: IssueStatus.INITIALIZED,
  }, {
    $set: {
      status: IssueStatus.AGGREGATOR_PENDING,
      aggregator: {
        stakingKey: requestBody.stakingKey,
        githubUsername: signatureData.githubUsername,
        roundNumber: signatureData.roundNumber,
      },
    },
  }, { new: true });
  if (notAssignedIssue) {
    res.status(200).json({
      success: true,
      role: "aggregator",
      issue_uuid: notAssignedIssue.issueUuid,
    });
    return;
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

    const inProcessIssues = await IssueModel.find({
      issueUuid: { $in: dependencyFinishedTodosUUID },
      status: IssueStatus.IN_PROCESS,
    });

    const inProcessIssueUUIDs = inProcessIssues.map(issue => issue.issueUuid);

    if (inProcessIssueUUIDs.length === 0) {
      res.status(404).json({
        success: false,
        message: "No in-process issues found",
      });
      return;
    }
    // Explain: The reason why I find again is to make it modular
    const updatedTodo = await TodoModel.findOneAndUpdate({
      // Not assigned to the current user
      issueUuid: { $in: inProcessIssueUUIDs },
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
    // Check if there is any issue in ASSIGN_PENDING status, if there is, return the issue uuid
    const assignPendingIssues = await IssueModel.find({
      status: IssueStatus.ASSIGN_PENDING,
    });

    const assignPendingIssueUUIDs = assignPendingIssues.map(issue => issue.issueUuid);


    // return the aggregator info for the todo as well
    const chosenTODOIssue = await IssueModel.findOne({
      issueUuid: updatedTodo.issueUuid,
    });

    const aggregatorInfo = chosenTODOIssue?.aggregator;

    res.status(200).json({
      success: true,
      role: "worker",
      data: {
        title: updatedTodo.title,
        acceptance_criteria: updatedTodo.acceptanceCriteria,
        repo_owner: updatedTodo.repoOwner,
        repo_name: updatedTodo.repoName,
        system_prompt: process.env.SYSTEM_PROMPT,
        aggregator_info: aggregatorInfo,
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
