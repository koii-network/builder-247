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

  async function verifySignatureData(
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
  
export const addAggregatorInfo = async (req: Request, res: Response) => {
    const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.stakingKey, requestBody.pubKey, "addAggregatorInfo");
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  const issue = await IssueModel.findOneAndUpdate({
    issueUuid: signatureData.issueUuid,
    aggregator: {
      stakingKey: requestBody.stakingKey,
      githubUsername: signatureData.githubUsername,
      roundNumber: signatureData.roundNumber,
    },
  }, {
    $set: {
      status: IssueStatus.IN_PROCESS,
    },
  }, { new: true });
  if (!issue) {
    res.status(404).json({
      success: false,
      message: "Issue not found",
    });
    return;
  }

  issue.status = IssueStatus.IN_PROCESS;

  await issue.save();

  res.status(200).json({
    success: true,
    message: "Aggregator info added",
  });
};
