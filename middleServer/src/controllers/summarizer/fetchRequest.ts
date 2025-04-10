import { Request, Response } from "express";
import "dotenv/config";

import { DocumentationModel, DocumentationStatus } from "../../models/Documentation";
// import { documentSummarizerTaskID } from "../../config/constant";
import { isValidStakingKey } from "../../utils/taskState";
import { verifySignature } from "../../utils/sign";
import { documentSummarizerTaskID, SwarmBountyStatus, taskID } from "../../config/constant";
import { syncDB } from "../../services/summarizer/syncDB";
import { updateSwarmBountyStatus } from "../../services/swarmBounty/updateStatus";


// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string, roundNumber: number) {
  try {
    const result = await DocumentationModel.findOne({
      assignedTo: {
        $elemMatch: {
          taskId: documentSummarizerTaskID,
          stakingKey: stakingKey,
          roundNumber: roundNumber,
        },
      },
    })
      .lean();

    if (!result) return null;

    // Find the specific assignment entry
    const assignment = result.assignedTo.find(
      (a: any) => a.stakingKey === stakingKey && a.roundNumber === roundNumber && a.taskId === documentSummarizerTaskID,
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
      body.taskId !== documentSummarizerTaskID ||
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
export const preProcessTodoLogic = async () => {
  await syncDB();
  await updateFailedPlannerTask();
}
export const updateFailedPlannerTask = async () => {
  const docs = await DocumentationModel.find({ assignedTo: { $size: 5 } });
  for (const doc of docs) {
    doc.status = DocumentationStatus.FAILED;
    await doc.save();
    await updateSwarmBountyStatus(doc.swarmBountyId, SwarmBountyStatus.FAILED);
    
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

  if (!(await isValidStakingKey(documentSummarizerTaskID, requestBody.stakingKey))) {
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
  await preProcessTodoLogic();
  const existingAssignment = await checkExistingAssignment(requestBody.stakingKey, signatureData.roundNumber);
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
              repo_owner: existingAssignment.spec.repoOwner,
              repo_name: existingAssignment.spec.repoName,
            },
          }};
      }
  }

  try {
    
    const updatedTodo = await DocumentationModel.findOneAndUpdate(
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
                      { taskId: documentSummarizerTaskID }
                    ]
                  },
                  { taskId: { $ne: documentSummarizerTaskID } }
                ]
              },
              { status: DocumentationStatus.IN_PROGRESS }
            ]
          },
          { $and: [{ status: DocumentationStatus.INITIALIZED }] }
        ]
      },
      {
        $push: {
          assignedTo: {
            stakingKey: requestBody.stakingKey,
            taskId: documentSummarizerTaskID,
            roundNumber: signatureData.roundNumber,
            githubUsername: signatureData.githubUsername,
            todoSignature: requestBody.signature
          }
        },
        $set: {
          status: DocumentationStatus.IN_PROGRESS,
          taskId: documentSummarizerTaskID,
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
    try {
      await updateSwarmBountyStatus(updatedTodo.swarmBountyId, SwarmBountyStatus.ASSIGNED);
    } catch (error) {
      console.error("Error updating swarm bounty status:", error);
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

// async function test(){
//   const docs = await fetchTodoLogic({signature: "0x123", stakingKey: "0x123"}, {roundNumber: 1, githubUsername: "0x123"});
//   console.log(docs);
// }

// test();