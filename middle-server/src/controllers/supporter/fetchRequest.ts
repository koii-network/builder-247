import { Request, Response } from "express";
import "dotenv/config";
import { StarFollowModel } from "../../models/StarFollow";
import { verifySignature } from "../../utils/sign";
import { SUPPORTER_TASK_ID, SwarmBountyStatus } from "../../config/constant";
import { isValidStakingKey } from "../../utils/taskState";
import { getSwarmBounty } from "../../utils/prometheus/api";
import { Bounty } from "../../types/bounty";
// import { updateSwarmBountyStatus } from "../../services/swarmBounty/updateStatus";

// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string, roundNumber: number) {
  try {
    const result = await StarFollowModel.findOne({
        stakingKey: stakingKey,
        taskId: process.env.SUPPORTER_TASK_ID,
        roundNumber: roundNumber,
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
      body.taskId !== SUPPORTER_TASK_ID ||
      body.action !== action ||
      !body.githubUsername ||
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
  const response = await fetchTodoLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);

 
};


export const fetchTodoLogic = async (requestBody: {signature: string, stakingKey: string}, signatureData: {roundNumber: number, githubUsername: string}): Promise<{statuscode: number, data: any}> => {
  const existingAssignment = await checkExistingAssignment(requestBody.stakingKey, signatureData.roundNumber);
  if (existingAssignment) {

        return {statuscode: 200, data:{
            success: true,
            data: {
                pendingRepos: existingAssignment
            }
        }
  }}

  try {
    const swarmBountyData = await getSwarmBounty();
    if (!swarmBountyData) {
      return {statuscode: 500, data:{
        success: false,
        message: "Failed to fetch swarm bounty",
      }}
    }
    const repoUrls = swarmBountyData.data.map((bounty: Bounty) => bounty.githubUrl);
    // check repoUrls that not in StarFollowModel's 
    const updatedTodo = await StarFollowModel.findOneAndUpdate(
      {
        $or: [
                {
                $and: [
                    { roundNumber: { $lt: signatureData.roundNumber - 3 } },
                    { taskId: SUPPORTER_TASK_ID }
                ]
                },
                { taskId: { $ne: SUPPORTER_TASK_ID } }
        ]
      },
      {
        $set: {
          taskId: SUPPORTER_TASK_ID,
          roundNumber: signatureData.roundNumber,
        }
      },
      { new: true }
    ).sort({ createdAt: 1 }).exec();
    
    if (!updatedTodo) {
      return {statuscode: 404, data:{
        success: false,
        message: "No available todos found",
      }};
    }


    return {statuscode: 200, data:{
      success: true,
      
    }};
  } catch (error) {
    console.error("Error fetching todos:", error);
    return {statuscode: 500, data:{
      success: false,
      message: "Failed to fetch todos",
    }}
  }
}

// async function test(){
//   const docs = await fetchTodoLogic({signature: "0x123", stakingKey: "0x123"}, {roundNumber: 1, githubUsername: "0x123"});
//   console.log(docs);
// }

// test();