import { request, Request, Response } from "express";
import { TodoModel } from "../models/Todo";
import { verifySignature } from "../utils/sign";
import { taskIDs } from "../constant";
import { isValidStakingKey } from "../utils/taskState";

// Helper function to verify request body
function verifyRequestBody(req: Request): {
  signature: string;
  stakingKey: string;
  pubKey: string;
} | null {
  try {
    console.log("Request body:", req.body);
    const signature = req.body.signature as string;
    const stakingKey = req.body.stakingKey as string;
    const pubKey = req.body.pubKey as string;
    if (!signature || !stakingKey || !pubKey) {
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
  stakingKey: string,
  pubKey: string,
): Promise<{ roundNumber: string; githubUsername: string; prUrl: string; taskId: string } | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log("Signature verification failed:", error);
      return null;
    }
    const body = JSON.parse(data);
    console.log("Signature payload:", body);

    // Log all validation checks
    console.log({
      taskIDFromEnv: taskIDs,
      taskIdFromPayload: body.taskId,
      roundNumberValue: body.roundNumber,
      githubUsername: body.githubUsername,
      pubKey: body.pubKey,
      stakingKey: body.stakingKey,
      prUrl: body.prUrl,
      taskIDMatch: taskIDs.includes(body.taskId),
      roundNumberTypeMatch: typeof body.roundNumber === "number",
      actionMatch: body.action === "audit",
      pubKeyMatch: body.pubKey === pubKey,
      stakingKeyMatch: body.stakingKey === stakingKey,
    });

    if (
      !body.taskId ||
      typeof body.roundNumber !== "number" ||
      !taskIDs.includes(body.taskId) ||
      body.action !== "audit" ||
      !body.prUrl ||
      !body.githubUsername ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      console.log("Signature payload validation failed");
      return null;
    }
    return {
      roundNumber: body.roundNumber,
      githubUsername: body.githubUsername,
      prUrl: body.prUrl,
      taskId: body.taskId,
    };
  } catch (error) {
    console.error("Error in verifySignatureData:", error);
    return null;
  }
}

async function checkToDoAssignment(stakingKey: string, githubUsername: string, prUrl: string): Promise<boolean> {
  try {
    const result = await TodoModel.findOne({
      assignedStakingKey: stakingKey,
      assignedGithubUsername: githubUsername,
      prUrl: prUrl,
    })
      .select("_id")
      .lean();

    console.log("Todo assignment check result:", result);
    return result !== null;
  } catch (error) {
    console.error("Error checking todo assignment:", error);
    return false;
  }
}

export const checkToDo = async (req: Request, res: Response) => {
  console.log("\nProcessing check-to-do request");
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    console.log("Invalid request body");
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.stakingKey, requestBody.pubKey);
  if (!signatureData) {
    console.log("Failed to verify signature data");
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  if (!(await isValidStakingKey(requestBody.stakingKey, signatureData.taskId))) {
    console.log("Invalid staking key:", requestBody.stakingKey);
    res.status(401).json({
      success: false,
      message: "Invalid staking key",
    });
    return;
  }

  const isValid = await checkToDoAssignment(requestBody.stakingKey, signatureData.githubUsername, signatureData.prUrl);

  if (!isValid) {
    console.log("No matching todo assignment found");
    res.status(404).json({
      success: false,
      message: "No matching todo assignment found",
    });
    return;
  }

  console.log("Todo assignment verified successfully");
  res.status(200).json({
    success: true,
    message: "Todo assignment verified successfully",
  });
};
