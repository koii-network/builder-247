import { Request, Response } from "express";
import { IssueModel, IssueStatus } from "../models/Issue";
import { verifySignature } from "../utils/sign";
import { taskID } from "../constant";
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

async function verifySignatureData /*  */(
  signature: string,
  stakingKey: string,
  pubKey: string,
  action: string,
): Promise<{ roundNumber: number; githubUsername: string; issueUuid: string } | null> {
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
      body.taskId !== taskID ||
      body.action !== action ||
      !body.githubUsername ||
      !body.issueUuid ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      console.log("bad signature data");
      return null;
    }
    return { roundNumber: body.roundNumber, githubUsername: body.githubUsername, issueUuid: body.issueUuid };
  } catch (error) {
    console.log("unexpected signature error", error);
    return null;
  }
}

export const assignIssue = async (req: Request, res: Response) => {
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
    "assignIssue",
  );
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  const response = await assignIssueLogic(signatureData);
  res.status(response.statuscode).json(response.data);
};

export const assignIssueLogic = async (signatureData: {
  roundNumber: number;
  githubUsername: string;
  issueUuid: string;
}) => {
  const fiveMinutesAgo = new Date(Date.now() - 300000); // 5 minutes in milliseconds

  const [result] = await IssueModel.aggregate([
    {
      $facet: {
        activeCheck: [
          {
            $match: {
              $or: [
                { status: IssueStatus.IN_PROCESS },
                {
                  $and: [{ status: IssueStatus.AGGREGATOR_PENDING }, { updatedAt: { $gt: fiveMinutesAgo } }],
                },
              ],
            },
          },
          { $limit: 1 },
        ],
        nextIssue: [
          {
            $match: {
              $or: [
                { status: IssueStatus.INITIALIZED },
                {
                  $and: [{ status: IssueStatus.AGGREGATOR_PENDING }, { updatedAt: { $lt: fiveMinutesAgo } }],
                },
              ],
            },
          },
          { $sort: { createdAt: 1 } },
          { $limit: 1 },
        ],
      },
    },
    {
      $project: {
        hasActive: { $gt: [{ $size: "$activeCheck" }, 0] },
        nextIssue: { $arrayElemAt: ["$nextIssue", 0] },
      },
    },
  ]);

  if (result.hasActive) {
    return {
      statuscode: 400,
      data: {
        success: false,
        message: "Issue is already in process",
      },
    };
  }
  if (!result.nextIssue) {
    return {
      statuscode: 404,
      data: {
        success: false,
        message: "No issue found",
      },
    };
  }

  await IssueModel.findByIdAndUpdate(
    result.nextIssue._id,
    {
      $set: { status: IssueStatus.IN_PROCESS },
    },
    { new: true },
  );

  return {
    statuscode: 200,
    data: {
      success: true,
      message: "Issue assigned",
    },
  };
};
