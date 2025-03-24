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
  ): Promise<{ roundNumber: number; prUrl: string; issueUuid: string } | null> {
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
      return { roundNumber: body.roundNumber, prUrl: body.prUrl, issueUuid: body.issueUuid };
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

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.stakingKey, requestBody.pubKey, "addIssuePR");
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
export const addIssuePRLogic = async (requestBody: {signature: string, stakingKey: string, pubKey: string}, signatureData: {roundNumber: number, prUrl: string, issueUuid: string}) => {

const issue = await IssueModel.findOneAndUpdate({
    issueUuid: signatureData.issueUuid,
    leaderDecidedRound: signatureData.roundNumber,
  }, {
    $push: {
      assignedTo: {
        stakingKey: requestBody.stakingKey,
        pubkey: requestBody.pubKey,
        taskId: taskID,
        roundNumber: signatureData.roundNumber,
        githubUsername: "koii-network",
        prUrl: signatureData.prUrl,
      },
    },
  }, { new: true });
  if (!issue) {
    return {statuscode: 404, data:{
      success: false,
      message: "Issue not found",
    }};
  }

  await issue.save();

  return {statuscode: 200, data:{
    success: true,
    message: "Issue PR added",
  }};
}