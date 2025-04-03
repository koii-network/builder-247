import { Request, Response } from "express";
import { IssueModel, IssueStatus } from "../models/Issue";
import { verifySignature } from "../utils/sign";
import { taskIDs } from "../constant";
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
): Promise<{ roundNumber: number; prUrl: string; issueUuid: string; taskId: string } | null> {
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
      !taskIDs.includes(body.taskId) ||
      body.action !== action ||
      !body.prUrl ||
      !body.issueUuid ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      console.log("bad signature data");
      return null;
    }
    return {
      roundNumber: body.roundNumber,
      prUrl: body.prUrl,
      issueUuid: body.issueUuid,
      taskId: body.taskId,
    };
  } catch (error) {
    console.log("unexpected signature error", error);
    return null;
  }
}

export const addIssuePR = async (req: Request, res: Response) => {
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
    "add-issue-pr",
  );
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  const response = await addIssuePRLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);
};
export const addIssuePRLogic = async (
  requestBody: { signature: string; stakingKey: string; pubKey: string },
  signatureData: { roundNumber: number; prUrl: string; issueUuid: string },
) => {
  const issue = await IssueModel.findOneAndUpdate(
    {
      issueUuid: signatureData.issueUuid,
      leaderDecidedRound: signatureData.roundNumber,
    },
    {
      assignedStakingKey: requestBody.stakingKey,
      assignedPubKey: requestBody.pubKey,
      assignedRoundNumber: signatureData.roundNumber,
      prUrl: signatureData.prUrl,
      status: IssueStatus.IN_REVIEW,
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

  return {
    statuscode: 200,
    data: {
      success: true,
      message: "Issue PR added",
    },
  };
};
