import { TodoModel } from "../models/Todo";

import { Request, Response } from "express";
import { verifySignature } from "../utils/sign";
import { taskID } from "../constant";
import { isValidStakingKey } from "../utils/taskState";

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
): Promise<{ roundNumber: number; prUrl: string } | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      return null;
    }
    const body = JSON.parse(data);
    if (
      !body.taskId ||
      body.taskId !== taskID ||
      typeof body.roundNumber !== "number" ||
      body.action !== "add" ||
      !body.prUrl ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
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
async function updateAssignedInfoWithPRUrl(
  stakingKey: string,
  roundNumber: number,
  prUrl: string,
  prSignature: string,
): Promise<boolean> {
  const result = await TodoModel.findOneAndUpdate(
    {
      assignedTo: {
        $elemMatch: {
          stakingKey: stakingKey,
          roundNumber: roundNumber,
        },
      },
    },
    {
      $set: { "assignedTo.$.prUrl": prUrl, "assignedTo.$.prSignature": prSignature },
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

  console.log("prUrl", signatureData.prUrl);
  const result = await updateAssignedInfoWithPRUrl(
    requestBody.pubKey,
    signatureData.roundNumber,
    signatureData.prUrl,
    requestBody.signature,
  );
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
