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
  const response = await fetchTodoLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);

 
};


export const fetchTodoLogic = async (requestBody: {signature: string, stakingKey: string, pubKey: string}, signatureData: {roundNumber: number, githubUsername: string}) => {
  // Update Assign Pending Issues
  const assignPendingIssues = await IssueModel.find({
    status: IssueStatus.ASSIGN_PENDING,
    $or: [
      { leaderDecidedRound: { $exists: false } },
      { leaderDecidedRound: signatureData.roundNumber }
    ]
  });

  const assignPendingIssueUUIDs = assignPendingIssues.map(issue => issue.issueUuid);

  await IssueModel.updateMany(
    { 
      status: IssueStatus.ASSIGN_PENDING,
      $or: [
        { leaderDecidedRound: { $exists: false } },
        { leaderDecidedRound: signatureData.roundNumber }
      ]
    },
    { $set: { leaderDecidedRound: signatureData.roundNumber } }
  );

  const existingAssignment = await checkExistingAssignment(requestBody.pubKey, signatureData.roundNumber);
  // Whether we need a leader 

  if (existingAssignment) {
    if (existingAssignment.hasPR) {
      return {statuscode: 401, data:{
        success: false,
        message: "Task already completed",
      }};
    } else {

      const chosenTODOIssue = await IssueModel.findOne({
        issueUuid: existingAssignment.todo.issueUuid,
      });

      const aggregatorInfo = chosenTODOIssue?.aggregator;

      const dependencyTaskPRUrls = [];
      for (const dependency of existingAssignment.todo.dependencyTasks) {
        const dependencyTask = await TodoModel.findOne({
          uuid: dependency,
        });
        
        const firstValidAssignment = dependencyTask?.assignedTo.find((assignment: any) => assignment.prUrl);
        dependencyTaskPRUrls.push(firstValidAssignment?.prUrl);
      }
      return {statuscode: 200, data:{
        success: true,
        role: "worker",
        data: {
          title: existingAssignment.todo.title,
          acceptance_criteria: existingAssignment.todo.acceptanceCriteria,
          repo_owner: existingAssignment.todo.repoOwner,
          repo_name: existingAssignment.todo.repoName,
          system_prompt: process.env.SYSTEM_PROMPT,
          aggregator_info: aggregatorInfo,
          assignPendingIssueUUIDs: assignPendingIssueUUIDs,
          dependencyTaskPRUrls: dependencyTaskPRUrls,
        },
      }};
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
    return {statuscode: 200, data:{
      success: true,
      role: "aggregator",
      issue_uuid: notAssignedIssue.issueUuid,
      assignPendingIssueUUIDs: assignPendingIssueUUIDs,
    }};
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
          uuid: dependency,
          status: TodoStatus.AUDITED,
        });
        if (!dependencyFinishedTodo) {
          isDependencyFinished = false;
          break;
        }
      }
      if (isDependencyFinished) {
        dependencyFinishedTodosUUID.push(todo.uuid);
      }
    }

    if (todos.length === 0 || dependencyFinishedTodosUUID.length === 0) {
      if (assignPendingIssueUUIDs.length === 0) {
        return {statuscode: 404, data:{
          success: false,
          message: `No todos available, todos: ${todos.length}, dependencyFinishedTodosUUID: ${dependencyFinishedTodosUUID.length}`,
        }};
      } else {
        return {statuscode: 200, data:{
          success: true,
          role: "worker",
          assignPendingIssueUUIDs: assignPendingIssueUUIDs,
        }};
      }
    }
    console.log("todos listed:", todos.length);

    const inProcessIssues = await IssueModel.find({
      status: IssueStatus.IN_PROCESS,
    });

    const inProcessIssueUUIDs = inProcessIssues.map(issue => issue.issueUuid);

    if (inProcessIssueUUIDs.length === 0) {
      if (assignPendingIssueUUIDs.length === 0) {
        return {statuscode: 404, data:{
          success: false,
          message: "No in-process issues found",
        }};
      } else {
        return {statuscode: 200, data:{
          success: true,
          role: "worker",
          assignPendingIssueUUIDs: assignPendingIssueUUIDs,
        }};
      }
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
        uuid: { $in: dependencyFinishedTodosUUID },
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
      return {statuscode: 409, data:{
        success: false,
        message: "Task assignment conflict",
      }};
    }
    // Dependency Task PR URLs
    const dependencyTaskPRUrls = [];
    for (const dependency of updatedTodo.dependencyTasks) {
      const dependencyTask = await TodoModel.findOne({
        uuid: dependency,
      });
      
      const firstValidAssignment = dependencyTask?.assignedTo.find((assignment: any) => assignment.prUrl);
      dependencyTaskPRUrls.push(firstValidAssignment?.prUrl);
    }
    // Elect Leader/Aggregator Node Part
    // Check all issues if there is any issue in ASSIGN_PENDING status, if there is, return the issue uuid
    // Check if there is any issue in ASSIGN_PENDING status, if there is, return the issue uuid
    // TODO: We need to reassign an issue when the round number is < current round number - 4


    // return the aggregator info for the todo as well
    const chosenTODOIssue = await IssueModel.findOne({
      issueUuid: updatedTodo.issueUuid,
    });

    const aggregatorInfo = chosenTODOIssue?.aggregator;

    return {statuscode: 200, data:{
      success: true,
      role: "worker",
      data: {
        title: updatedTodo.title,
        acceptance_criteria: updatedTodo.acceptanceCriteria,
        repo_owner: updatedTodo.repoOwner,
        repo_name: updatedTodo.repoName,
        system_prompt: process.env.SYSTEM_PROMPT,
        aggregator_info: aggregatorInfo,
        dependencyTaskPRUrls: dependencyTaskPRUrls,
        assignPendingIssueUUIDs: assignPendingIssueUUIDs,
      },
    }};
  } catch (error) {
    console.error("Error fetching todos:", error);
    return {statuscode: 500, data:{
      success: false,
      message: "Failed to fetch todos",
    }}
  }
}