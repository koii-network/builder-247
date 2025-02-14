import { TodoModel } from "../models/Todo";

import { Request, Response } from "express";
import { verifySignature } from "../utils/sign";
import { taskID } from "../constant";
import { isValidStakingKey } from "../utils/taskState";

function verifyRequestBody(req: Request): { signature: string; pubKey: string; prUrl: string } | null {
  try {
    console.log("req.body", req.body);
    const signature = req.body.signature as string;
    const pubKey = req.body.pubKey as string;
    const prUrl = req.body.prUrl as string;
    if (!signature || !pubKey || !prUrl) {
      return null;
    }
    return { signature, pubKey, prUrl };
  } catch {
    return null;
  }
}

// Helper function to verify signature
async function verifySignatureData(signature: string, pubKey: string): Promise<{ roundNumber: number } | null> {
  try {
    const { data, error } = await verifySignature(signature, pubKey);
    if (error || !data) {
      return null;
    }
    const body = JSON.parse(data);
    if (!body.taskId || typeof body.roundNumber !== "number" || body.taskId !== taskID) {
      return null;
    }
    return { roundNumber: body.roundNumber };
  } catch {
    return null;
  }
}
async function updateAssignedInfoWithPRUrl(stakingKey: string, roundNumber: number, prUrl: string): Promise<boolean> {
  const result = await TodoModel.findOneAndUpdate(
    {
      "assignedTo.stakingKey": stakingKey,
      "assignedTo.roundNumber": roundNumber,
    },
    {
      $set: { "assignedTo.$.prUrl": prUrl },
    },
  )
    .select("_id")
    .lean();

  return result !== null;
}

export const addPR = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.pubKey);
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  if (!(await isValidStakingKey(requestBody.pubKey))) {
    res.status(401).json({
      success: false,
      message: "Invalid staking key",
    });
    return;
  }

  console.log("prUrl", requestBody.prUrl);
  const result = await updateAssignedInfoWithPRUrl(requestBody.pubKey, signatureData.roundNumber, requestBody.prUrl);
  if (!result) {
    res.status(401).json({
      success: false,
      message: "Failed to update pull request URL",
    });
    return;
  }

  res.status(200).json({
    success: true,
    message: "Pull request URL updated",
  });
};
