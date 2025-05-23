import { DocumentationModel } from "../../models/Documentation";

import { Request, Response } from "express";
import { verifySignature } from "../../utils/sign";
import { documentSummarizerTaskID, SwarmBountyStatus } from "../../config/constant";
import { isValidStakingKey } from "../../utils/taskState/stakingList";
import { updateSwarmBountyStatus } from "../../services/swarmBounty/updateStatus";

function verifyRequestBody(req: Request): { signature: string; stakingKey: string } | null {
  try {
    console.log("req.body", req.body);
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

// Helper function to verify signature
async function verifySignatureData(
  signature: string,
  stakingKey: string,
): Promise<{ roundNumber: number; prUrl: string } | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log("signature error", error);
      return null;
    }
    const body = JSON.parse(data);
    console.log("signature payload", { body, stakingKey });
    if (
      !body.taskId ||
      body.taskId !== documentSummarizerTaskID ||
      typeof body.roundNumber !== "number" ||
      body.action !== "add" ||
      !body.prUrl ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      return null;
    }
    return { roundNumber: body.roundNumber, prUrl: body.prUrl };
  } catch {
    return null;
  }
}
async function updateAssignedInfoPrUrl(
  stakingKey: string,
  roundNumber: number,
  prUrl: string,
  signature: string,
): Promise<boolean> {
  console.log("updateAssignedInfoWithIPFS", { stakingKey, roundNumber, prUrl, signature });
  const result = await DocumentationModel.findOneAndUpdate(
    {
      assignedTo: {
        $elemMatch: {
          taskId: documentSummarizerTaskID,
          stakingKey: stakingKey,
          roundNumber: roundNumber,
        },
      },            
    },
    {
      $set: { "assignedTo.$.prUrl": prUrl },
    },
  )
    .select("_id")
    .lean();
    try{
      if (result?.swarmBountyId) {
        await updateSwarmBountyStatus(result?.swarmBountyId, SwarmBountyStatus.AUDITING);
      }
    } catch (error) {
      console.error("Error updating swarm bounty status:", error);
    }
  console.log("prUrl update result", result);

  return result !== null;
}

export const addRequest = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.stakingKey);
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

  const response = await addPRUrlLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);
};

export const addPRUrlLogic = async (requestBody: {signature: string, stakingKey: string}, signatureData: {roundNumber: number, prUrl: string}) => {
  console.log("prUrl", signatureData.prUrl);
  const result = await updateAssignedInfoPrUrl(
    requestBody.stakingKey,
    signatureData.roundNumber,
    signatureData.prUrl,
    requestBody.signature,
  );
  if (!result) {
    return {statuscode: 401, data:{
      success: false, 
      message: "Failed to update PR URL",
    }};
  }

  return {statuscode: 200, data:{
    success: true,
    message: "PR URL updated",
  }};
};

// async function test(){
//     const docs = await addPRUrlLogic({signature: "0x123", stakingKey: "0x123"}, {roundNumber: 1, prUrl: "0x123"});
//     console.log(docs);
//   }
  
//   test();