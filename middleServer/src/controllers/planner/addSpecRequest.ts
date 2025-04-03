import { SpecModel } from "../../models/Spec";

import { Request, Response } from "express";
import { verifySignature } from "../../utils/sign";
import { taskID } from "../../config/constant";
import { isValidStakingKey } from "../../utils/taskState";

function verifyRequestBody(req: Request): { signature: string; pubKey: string; stakingKey: string } | null {
  try {
    console.log("req.body", req.body);
    const signature = req.body.signature as string;
    const pubKey = req.body.pubKey as string;
    const stakingKey = req.body.stakingKey as string;
    if (!signature || !pubKey || !stakingKey) {
      return null;
    }

    return { signature, pubKey, stakingKey };
  } catch {
    return null;
  }
}

// Helper function to verify signature
async function verifySignatureData(
  signature: string,
  pubKey: string,
  stakingKey: string,
): Promise<{ roundNumber: number; ipfsCid: string } | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log("signature error", error);
      return null;
    }
    const body = JSON.parse(data);
    console.log("signature payload", { body, pubKey, stakingKey });
    if (
      !body.taskId ||
      body.taskId !== taskID ||
      typeof body.roundNumber !== "number" ||
      body.action !== "add" ||
      !body.ipfsCid ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      return null;
    }
    return { roundNumber: body.roundNumber, ipfsCid: body.ipfsCid };
  } catch {
    return null;
  }
}
async function updateAssignedInfoWithIPFS(
  stakingKey: string,
  roundNumber: number,
  ipfsCid: string,
  ipfsSignature: string,
): Promise<boolean> {
  console.log("updateAssignedInfoWithIPFS", { stakingKey, roundNumber, ipfsCid, ipfsSignature });
  const result = await SpecModel.findOneAndUpdate(
    {
      assignedTo: {
        $elemMatch: {
          taskId: taskID,
          stakingKey: stakingKey,
          roundNumber: roundNumber,
        },
      },
    },
    {
      $set: { "assignedTo.$.ipfsCid": ipfsCid, "assignedTo.$.ipfsSignature": ipfsSignature },
    },
  )
    .select("_id")
    .lean();

  console.log("ipfsCid update result", result);

  return result !== null;
}

export const addIPFS = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.pubKey, requestBody.stakingKey);
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

  const response = await addIPFSLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);
};

export const addIPFSLogic = async (requestBody: {signature: string, pubKey: string, stakingKey: string}, signatureData: {roundNumber: number, ipfsCid: string}) => {
  console.log("ipfsCid", signatureData.ipfsCid);
  const result = await updateAssignedInfoWithIPFS(
    requestBody.stakingKey,
    signatureData.roundNumber,
    signatureData.ipfsCid,
    requestBody.signature,
  );
  if (!result) {
    return {statuscode: 401, data:{
      success: false, 
      message: "Failed to update IPFS CID",
    }};
  }

  return {statuscode: 200, data:{
    success: true,
    message: "IPFS CID updated",
  }};
};
