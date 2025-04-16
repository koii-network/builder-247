import { Request, Response } from "express";
import { StarFollowModel } from "../../models/StarFollow";
import { verifySignature } from "../../utils/sign";
import { SUPPORTER_TASK_ID } from "../../config/constant";
import { isValidStakingKey } from "../../utils/taskState";

// Helper function to verify request body
function verifyRequestBody(req: Request): {
  stakingKey: string;
  roundNumber: string;
  githubUsername: string;
  prUrl: string;
} | null {
  try {
    console.log("Request body:", req.body);

    const stakingKey = req.body.stakingKey as string;
    const roundNumber = req.body.roundNumber as string;
    const githubUsername = req.body.githubUsername as string;
    const prUrl = req.body.prUrl as string;
    if (!stakingKey || !roundNumber || !githubUsername || !prUrl) {
      return null;
    }
    return {  stakingKey, roundNumber, githubUsername, prUrl };
  } catch {
    return null;
  }
}



async function checkStarFollowAssignment(
  stakingKey: string,
  roundNumber: string,
): Promise<boolean> {
  try {
    const result = await StarFollowModel.findOne({
      stakingKey,
      taskId: SUPPORTER_TASK_ID,
      roundNumber,
      pendingRepos: { $ne: [] }
    });

    return result !== null;
  } catch (error) {
    console.error("Error checking star follow assignment:", error);
    return false;
  }
}

export const checkRequest = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }
  const isValid = await checkStarFollowAssignment(
    requestBody.stakingKey,
    requestBody.roundNumber,
  );

  if (!isValid) {
    res.status(404).json({
      success: false,
      message: "No matching todo assignment found",
    });
    return;
  }

  res.status(200).json({
    success: true,
    message: "Todo assignment verified successfully",
  });
};


