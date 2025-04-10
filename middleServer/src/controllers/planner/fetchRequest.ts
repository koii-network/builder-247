import { Request, Response } from "express";
import "dotenv/config";

import { SpecModel, SpecStatus } from "../../models/Spec";

import { isValidStakingKey } from "../../utils/taskState";
import { verifySignature } from "../../utils/sign";
import { plannerTaskID, SwarmBountyStatus } from "../../config/constant";
import { syncDB } from "../../services/planner/syncDB";
import { updateSwarmBountyStatus } from "../../services/swarmBounty/updateStatus";


// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string, roundNumber: number) {
  try {
    const result = await SpecModel.findOne({
      assignedTo: {
        $elemMatch: {
          taskId: plannerTaskID,
          stakingKey: stakingKey,
          roundNumber: roundNumber,
        },
      },
    })

      .lean();

    if (!result) return null;

    // Find the specific assignment entry
    const assignment = result.assignedTo.find(
      (a: any) => a.stakingKey === stakingKey && a.roundNumber === roundNumber && a.taskId === plannerTaskID,
    );

    return {
      spec: result,
      hasPR: Boolean(assignment?.prUrl),
    };
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
      body.taskId !== plannerTaskID ||
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

  if (!(await isValidStakingKey(plannerTaskID, requestBody.stakingKey))) {
    res.status(401).json({
      success: false,
      message: "Invalid staking key",
    });
    return;
  }
  const response = await fetchTodoLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);

 
};

export const preProcessTodoLogic = async () => {
  await syncDB();
  await updateFailedPlannerTask();
}
export const updateFailedPlannerTask = async () => {
  const specs = await SpecModel.find({ assignedTo: { $size: 5 } });
  for (const spec of specs) {
    spec.status = SpecStatus.FAILED;

    await updateSwarmBountyStatus(spec.swarmBountyId, SwarmBountyStatus.FAILED);
    
  }
}
export const fetchTodoLogic = async (requestBody: {signature: string, stakingKey: string}, signatureData: {roundNumber: number, githubUsername: string}): Promise<{statuscode: number, data: any}> => {
  await preProcessTodoLogic();
  const existingAssignment = await checkExistingAssignment(requestBody.stakingKey, signatureData.roundNumber);
  if (existingAssignment) {
    if (existingAssignment.hasPR) {
        return {statuscode: 401, data:{
          success: false,
          message: "Task already completed",
        }};
      }else{
        console.log("existingAssignment", existingAssignment);
        return {statuscode: 200, data:{
            success: true,
            role: "worker",
            data: {
              repo_owner: existingAssignment.spec.repoOwner,
              repo_name: existingAssignment.spec.repoName,
              description: existingAssignment.spec.description,
            },
          }};
      }
  }

  try {
    
    const updatedTodo = await SpecModel.findOneAndUpdate(
      {
        // Not assigned to the current user
        $nor: [
          { "assignedTo.stakingKey": requestBody.stakingKey },
          { "assignedTo.githubUsername": signatureData.githubUsername }
        ],
        $or: [
          { 
            $and: [
              {
                $or: [
                  {
                    $and: [
                      { roundNumber: { $lt: signatureData.roundNumber - 3 } },
                      { taskId: plannerTaskID }
                    ]
                  },
                  { taskId: { $ne: plannerTaskID } }
                ]
              },
              { status: SpecStatus.IN_PROGRESS }
            ]
          },
          { $and: [{ status: SpecStatus.INITIALIZED }] }
        ]
      },
      {
        $push: {
          assignedTo: {
            stakingKey: requestBody.stakingKey,
            taskId: plannerTaskID,
            roundNumber: signatureData.roundNumber,
            githubUsername: signatureData.githubUsername,
            todoSignature: requestBody.signature
          }
        },
        $set: {
          status: SpecStatus.IN_PROGRESS,
          taskId: plannerTaskID,
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

    // Validate required data fields
    if (!updatedTodo.repoOwner || !updatedTodo.repoName) {
      return {statuscode: 404, data:{
        success: false,
        message: "Todo data is incomplete",
      }};
    }

    return {statuscode: 200, data:{
      success: true,
      role: "worker",
      data: {
        repo_owner: updatedTodo.repoOwner,
        repo_name: updatedTodo.repoName,
        description: updatedTodo.description,
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


// export const test = async () => {
//   const response = await fetchTodoLogic({signature: "0x123", stakingKey: "0x123"}, {roundNumber: 2, githubUsername: "0x123"});
//   console.log(response);
// }

// test();
