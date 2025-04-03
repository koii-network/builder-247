import { TodoModel } from "../models/Todo";

import { Request, Response } from "express";
import { verifySignature } from "../utils/sign";
import { taskIDs } from "../constant";
import { isValidStakingKey } from "../utils/taskState";
import { TodoStatus } from "../models/Todo";

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
  action: string,
): Promise<{ roundNumber: number; prUrl: string; taskId: string } | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log("signature error", error);
      return null;
    }
    const body = JSON.parse(data);
    console.log("signature payload", { body, pubKey, stakingKey });
    console.log("taskIDs match", taskIDs.includes(body.taskId));
    console.log("typeof body.roundNumber", typeof body.roundNumber);
    console.log("body.action", body.action);
    console.log("body.pubKey", body.pubKey);
    console.log("body.stakingKey", body.stakingKey);
    if (
      !body.taskId ||
      !taskIDs.includes(body.taskId) ||
      typeof body.roundNumber !== "number" ||
      body.action !== action ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      return null;
    }
    return { roundNumber: body.roundNumber, prUrl: body.prUrl, taskId: body.taskId };
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
  console.log("updateAssignedInfoWithPRUrl", { stakingKey, roundNumber, prUrl, prSignature });
  const result = await TodoModel.findOneAndUpdate(
    {
      assignedStakingKey: stakingKey,
      assignedRoundNumber: roundNumber,
    },
    {
      $set: {
        prUrl: prUrl,
        status: TodoStatus.IN_REVIEW,
      },
    },
  )
    .select("_id")
    .lean();

  console.log("pr update result", result);

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

  const signatureData = await verifySignatureData(
    requestBody.signature,
    requestBody.pubKey,
    requestBody.stakingKey,
    "add-pr",
  );
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  if (!(await isValidStakingKey(requestBody.stakingKey, signatureData.taskId))) {
    res.status(401).json({
      success: false,
      message: "Invalid staking key",
    });
    return;
  }

  const response = await addPRLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);
};

export const addPRLogic = async (
  requestBody: { signature: string; pubKey: string; stakingKey: string },
  signatureData: { roundNumber: number; prUrl: string },
) => {
  console.log("prUrl", signatureData.prUrl);
  const result = await updateAssignedInfoWithPRUrl(
    requestBody.stakingKey,
    signatureData.roundNumber,
    signatureData.prUrl,
    requestBody.signature,
  );
  if (!result) {
    return {
      statuscode: 401,
      data: {
        success: false,
        message: "Failed to update pull request URL",
      },
    };
  }

  const updatedTodo = await TodoModel.findOneAndUpdate(
    {
      assignedStakingKey: requestBody.stakingKey,
      assignedRoundNumber: signatureData.roundNumber,
    },
    {
      $set: {
        prUrl: signatureData.prUrl,
        status: TodoStatus.IN_REVIEW,
      },
    },
    { new: true },
  );

  if (!updatedTodo) {
    return {
      statuscode: 401,
      data: {
        success: false,
        message: "Failed to update todo status",
      },
    };
  }

  return {
    statuscode: 200,
    data: {
      success: true,
      message: "Pull request URL updated",
    },
  };
};
