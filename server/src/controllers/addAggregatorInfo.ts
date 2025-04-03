import { Request, Response } from "express";
import { IssueModel, IssueStatus } from "../models/Issue";
import { verifySignature } from "../utils/sign";
import { taskIDs } from "../constant";
import { TodoModel } from "../models/Todo";

export function verifyRequestBody(req: Request): { signature: string; stakingKey: string; pubKey: string } | null {
  console.log("verifyRequestBody", req.body);
  try {
    const signature = req.body.signature as string;
    const stakingKey = req.body.stakingKey as string;
    const pubKey = req.body.pubKey as string;
    if (!signature || !stakingKey || !pubKey) {
      return null;
    }
    return { signature, stakingKey, pubKey };
  } catch {
    return null;
  }
}

async function verifySignatureData(
  signature: string,
  stakingKey: string,
  pubKey: string,
  action: string,
): Promise<{
  roundNumber: number;
  githubUsername: string;
  issueUuid: string;
  taskId: string;
  aggregatorUrl: string;
} | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log("bad signature");
      return null;
    }
    const body = JSON.parse(data);
    console.log({ signature_payload: body });
    console.log("task id matches", taskIDs.includes(body.taskId));
    console.log("round number is number", typeof body.roundNumber === "number");
    console.log("pub key matches", body.pubKey === pubKey);
    console.log("staking key matches", body.stakingKey === stakingKey);
    console.log("action matches", body.action === action);
    console.log("github username exists", body.githubUsername);
    console.log("aggregator url exists", body.aggregatorUrl);
    console.log("issue uuid exists", body.issueUuid);
    if (
      !body.taskId ||
      typeof body.roundNumber !== "number" ||
      !taskIDs.includes(body.taskId) ||
      body.action !== action ||
      !body.githubUsername ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey ||
      !body.aggregatorUrl ||
      !body.issueUuid
    ) {
      console.log("bad signature data");
      return null;
    }
    return {
      roundNumber: body.roundNumber,
      githubUsername: body.githubUsername,
      issueUuid: body.issueUuid,
      taskId: body.taskId,
      aggregatorUrl: body.aggregatorUrl,
    };
  } catch (error) {
    console.log("unexpected signature error", error);
    return null;
  }
}

export const addAggregatorInfo = async (req: Request, res: Response) => {
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
    requestBody.stakingKey,
    requestBody.pubKey,
    "create-repo",
  );
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  const response = await addAggregatorInfoLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);
};

export const addAggregatorInfoLogic = async (
  requestBody: { signature: string; stakingKey: string; pubKey: string },
  signatureData: { roundNumber: number; githubUsername: string; issueUuid: string; aggregatorUrl: string },
) => {
  console.log("Searching for issue with:", {
    issueUuid: signatureData.issueUuid,
  });
  const issue = await IssueModel.findOneAndUpdate(
    {
      issueUuid: signatureData.issueUuid,
    },
    {
      $set: {
        status: IssueStatus.IN_PROCESS,
        aggregatorOwner: signatureData.githubUsername,
        aggregatorUrl: signatureData.aggregatorUrl,
      },
    },
    { new: true },
  );
  if (!issue) {
    return {
      statuscode: 404,
      data: {
        success: false,
        message: "Issue not found",
      },
    };
  }

  // Update all todos associated with this issue to use the aggregator owner
  // This ensures workers fork from the aggregator repo, not the original
  const todoUpdateResult = await TodoModel.updateMany(
    { issueUuid: signatureData.issueUuid },
    { $set: { repoOwner: signatureData.githubUsername } },
  );

  console.log("Updated todos for issue:", {
    issueUuid: signatureData.issueUuid,
    todosUpdated: todoUpdateResult.modifiedCount,
    aggregatorOwner: signatureData.githubUsername,
  });

  issue.status = IssueStatus.IN_PROCESS;

  await issue.save();

  return {
    statuscode: 200,
    data: {
      success: true,
      message: "Aggregator info added and todos updated",
      todosUpdated: todoUpdateResult.modifiedCount,
    },
  };
};
