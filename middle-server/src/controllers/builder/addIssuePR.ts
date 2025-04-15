import { Request, Response } from "express";
import { IssueModel, IssueStatus } from "../../models/Issue";
import { verifySignature } from "../../utils/sign";
import { taskIDs } from "../../config/constant";
export function verifyRequestBody(
  req: Request,
): { signature: string; stakingKey: string; pubKey: string; prUrl: string; issueUuid: string } | null {
  console.log("verifyRequestBody", req.body);
  try {
    const signature = req.body.signature as string;
    const stakingKey = req.body.stakingKey as string;
    const pubKey = req.body.pubKey as string;
    const prUrl = req.body.prUrl as string;
    const issueUuid = req.body.issueUuid as string;

    if (!signature || !stakingKey || !pubKey || !prUrl || !issueUuid) {
      return null;
    }
    return { signature, stakingKey, pubKey, prUrl, issueUuid };
  } catch {
    return null;
  }
}

async function verifySignatureData(
  signature: string,
  stakingKey: string,
  pubKey: string,
  action: string,
): Promise<{ roundNumber: number; taskId: string } | null> {
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

  const response = await addIssuePRLogic(requestBody, {
    roundNumber: signatureData.roundNumber,
    prUrl: requestBody.prUrl,
    issueUuid: requestBody.issueUuid,
  });
  res.status(response.statuscode).json(response.data);
};
export const addIssuePRLogic = async (
  requestBody: { signature: string; stakingKey: string; pubKey: string; prUrl: string; issueUuid: string },
  signatureData: { roundNumber: number; prUrl: string; issueUuid: string },
) => {
  const issue = await IssueModel.findOneAndUpdate(
    {
      issueUuid: signatureData.issueUuid,
    },
    {
      $push: {
        assignees: {
          stakingKey: requestBody.stakingKey,
          roundNumber: signatureData.roundNumber,
          prUrl: signatureData.prUrl,
        },
      },
      $set: {
        status: IssueStatus.IN_REVIEW,
      },
    },
    { new: true },
  );

  if (!issue) {
    return {
      statuscode: 409,
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
