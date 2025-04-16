import { Request, Response } from "express";
import "dotenv/config";
import { StarFollowModel } from "../../models/StarFollow";
import { verifySignature } from "../../utils/sign";
import { SUPPORTER_TASK_ID } from "../../config/constant";
import { isValidStakingKey } from "../../utils/taskState";
import { getSwarmBounty } from "../../utils/prometheus/api";
import { Bounty } from "../../types/bounty";
// import { updateSwarmBountyStatus } from "../../services/swarmBounty/updateStatus";

// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string) {
  try {
    const result = await StarFollowModel.findOne({
        stakingKey: stakingKey,
        taskId: process.env.SUPPORTER_TASK_ID,
        pendingRepos: { $ne: [] }
      },
    );

    if (!result) return null;

    // Find the specific assignment entry
    return result.pendingRepos;
  } catch (error) {
    console.error("Error checking assigned info:", error);
    return null;
  }
}
export function verifyRequestBody(req: Request): { signature: string; stakingKey: string } | null {
  try {
    const signature = req.body.signature as string;
    const stakingKey = req.body.stakingKey as string;
    if (!signature || !stakingKey) {
      return null;
    }
    return { signature, stakingKey };
  } catch {
    return null;
  }
}
async function verifySignatureData(
  signature: string,
  stakingKey: string,
  action: string,
): Promise<{ roundNumber: number } | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log("bad signature");
      return null;
    }
    const body = JSON.parse(data);
    console.log({ signature_payload: body });
    if (
      body.action !== action ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      console.log("bad signature data");
      return null;
    }
    return { roundNumber: body.roundNumber };
  } catch (error) {
    console.log("unexpected signature error", error);
    return null;
  }
}

export const fetchRequest = async (req: Request, res: Response) => {
  
  const requestBody: {signature: string, stakingKey: string} | null = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.stakingKey, "fetch");
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  if (!(await isValidStakingKey(SUPPORTER_TASK_ID, requestBody.stakingKey))) {
    res.status(401).json({
      success: false,
      message: "Invalid staking key",
    });
    return;
  }
  const response = await fetchTodoLogic(requestBody);
  res.status(response.statuscode).json(response.data);

 
};


export const fetchTodoLogic = async (requestBody: {signature: string, stakingKey: string}): Promise<{statuscode: number, data: any}> => {
  const existingAssignment = await checkExistingAssignment(requestBody.stakingKey);
  if (existingAssignment) {
    return {statuscode: 200, data:{
      success: true,
      data: {
        pendingRepos: existingAssignment
      }
    }}
  }

  try {
    const swarmBountyData = await getSwarmBounty();
    if (!swarmBountyData) {
      return {statuscode: 500, data:{
        success: false,
        message: "Failed to fetch swarm bounty",
      }}
    }
    const repoUrls = swarmBountyData.data.map((bounty: Bounty) => bounty.githubUrl);
    // If there are pending repos, no need to fetch new repos, just update task id and round number
    const existingPendingDoc = await StarFollowModel.findOne({ 
      stakingKey: requestBody.stakingKey,
      taskId: SUPPORTER_TASK_ID,
      pendingRepos: { $ne: [] }
    });
    if (existingPendingDoc) {
      return {statuscode: 200, data:{
        success: true,
        data: {
          pendingRepos: existingPendingDoc.pendingRepos
        }
      }}
    }
    // Find existing document
    const nonPendingDoc = await StarFollowModel.findOne({
      stakingKey: requestBody.stakingKey,
      $or: [
        {
          $and: [
            { taskId: SUPPORTER_TASK_ID }
          ]
        },
        { taskId: { $ne: SUPPORTER_TASK_ID } }
      ]
    }).sort({ createdAt: 1 });

    if (!nonPendingDoc) {
      return {statuscode: 404, data:{
        success: false,
        message: "No existing document found",
      }};
    }

    // Get existing pending and completed repos
    const existingPendingRepos = nonPendingDoc.pendingRepos || [];
    const existingCompletedRepos = nonPendingDoc.completedRepos || [];

    // Filter out repos that are already in pending or completed lists
    const newRepos = repoUrls.filter(
      (url: string) => 
        !existingPendingRepos.includes(url) && 
        !existingCompletedRepos.includes(url)
    );

    // Update the document with new repos and task info
    const updatedDoc = await StarFollowModel.findOneAndUpdate(
      { _id: nonPendingDoc._id },
      {
        $set: {
          taskId: SUPPORTER_TASK_ID,
          pendingRepos: [...existingPendingRepos, ...newRepos]
        }
      },
      { new: true }
    );

    if (!updatedDoc) {
      return {statuscode: 500, data:{
        success: false,
        message: "Failed to update document",
      }};
    }

    return {statuscode: 200, data:{
      success: true,
      data: {
        pendingRepos: updatedDoc.pendingRepos
      }
    }};
  } catch (error) {
    console.error("Error fetching repos:", error);
    return {statuscode: 500, data:{
      success: false,
      message: "Failed to fetch repos",
    }}
  }
}

