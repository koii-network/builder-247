import { Request, Response } from "express";
import "dotenv/config";

import { SpecModel, SpecStatus } from "../../models/Spec";
import { taskID } from "../../config/constant";
import { isValidStakingKey } from "../../utils/taskState";
import { verifySignature } from "../../utils/sign";



// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string, roundNumber: number) {
  try {
    const result = await SpecModel.findOne({
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
      spec: result,
      hasPR: Boolean(assignment?.ipfsCid),
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

  const existingAssignment = await checkExistingAssignment(requestBody.pubKey, signatureData.roundNumber);
  if (existingAssignment) {
    if (existingAssignment.hasPR) {
        return {statuscode: 401, data:{
          success: false,
          message: "Task already completed",
        }};
      }else{
        return {statuscode: 200, data:{
            success: true,
            role: "worker",
            data: {
              title: existingAssignment.spec.title,
              acceptance_criteria: existingAssignment.spec.description,
              repo_owner: existingAssignment.spec.repoOwner,
              repo_name: existingAssignment.spec.repoName,
              system_prompt: process.env.SYSTEM_PROMPT,
            },
          }};
      }
  }

  try {
    
    const updatedTodo = await SpecModel.findOneAndUpdate({
      // Not assigned to the current user
        $nor: [
          { "assignedTo.stakingKey": requestBody.pubKey },
          { "assignedTo.githubUsername": signatureData.githubUsername },
        ],
        $or: [
          { $and: [{ "assignedTo.roundNumber": { $lt: signatureData.roundNumber - 3 } }, { status: SpecStatus.IN_PROGRESS }] },
          { $and: [ { status: SpecStatus.INITIALIZED }] }
        ]
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
      status: SpecStatus.IN_PROGRESS,
    },
    { new: true },
  ).sort({ createdAt: 1 });

    if (!updatedTodo) {
      return {statuscode: 409, data:{
        success: false,
        message: "Task assignment conflict",
      }};
    }



    return {statuscode: 200, data:{
      success: true,
      role: "worker",
      data: {
        title: updatedTodo.title,
        acceptance_criteria: updatedTodo.description,
        repo_owner: updatedTodo.repoOwner,
        repo_name: updatedTodo.repoName,
        system_prompt: process.env.SYSTEM_PROMPT,
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