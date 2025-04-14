import { TodoModel } from "../models/Todo";

import { Request, Response } from "express";
import { verifySignature } from "../utils/sign";
<<<<<<<< HEAD:server/src/controllers/addTodoPR.ts
import { taskIDs } from "../constant";
========
import { taskID } from "../config/constant";
>>>>>>>> @planner-refine-task:middleServer/src/controllers/addTodoPR.ts
import { isValidStakingKey } from "../utils/taskState";
import { TodoStatus } from "../models/Todo";

function verifyRequestBody(
  req: Request,
): { signature: string; pubKey: string; stakingKey: string; prUrl: string; todo_uuid: string } | null {
  try {
    console.log("req.body", req.body);
    const signature = req.body.signature as string;
    const pubKey = req.body.pubKey as string;
    const stakingKey = req.body.stakingKey as string;
    const prUrl = req.body.prUrl as string;
    const todo_uuid = req.body.todo_uuid as string;
    if (!signature || !pubKey || !stakingKey || !prUrl || !todo_uuid) {
      return null;
    }

    return { signature, pubKey, stakingKey, prUrl, todo_uuid };
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
): Promise<{ roundNumber: number; taskId: string } | null> {
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
    return { roundNumber: body.roundNumber, taskId: body.taskId };
  } catch {
    return null;
  }
}

async function updateTodoWithPRUrl(
  todo_uuid: string,
  stakingKey: string,
  roundNumber: number,
  prUrl: string,
): Promise<boolean> {
  console.log("updateTodoWithPRUrl", { todo_uuid, stakingKey, roundNumber, prUrl });
  const result = await TodoModel.findOneAndUpdate(
    {
      uuid: todo_uuid,
    },
    {
      $set: {
        prUrl: prUrl,
        status: TodoStatus.IN_REVIEW,
        assignedStakingKey: stakingKey,
        assignedRoundNumber: roundNumber,
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
    "add-todo-pr",
  );
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

<<<<<<<< HEAD:server/src/controllers/addTodoPR.ts
  if (!(await isValidStakingKey(requestBody.stakingKey, signatureData.taskId))) {
========
  if (!(await isValidStakingKey(taskID, requestBody.stakingKey))) {
>>>>>>>> @planner-refine-task:middleServer/src/controllers/addTodoPR.ts
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
  requestBody: { signature: string; pubKey: string; stakingKey: string; prUrl: string; todo_uuid: string },
  signatureData: { roundNumber: number; taskId: string },
) => {
  console.log("prUrl", requestBody.prUrl);
  const result = await updateTodoWithPRUrl(
    requestBody.todo_uuid,
    requestBody.stakingKey,
    signatureData.roundNumber,
    requestBody.prUrl,
  );
  if (!result) {
    return {
      statuscode: 404,
      data: {
        success: false,
        message: "Todo not found",
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
