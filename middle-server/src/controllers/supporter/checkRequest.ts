import { Request, Response } from "express";
import { StarFollowModel } from "../../models/StarFollow";
import { verifySignature } from "../../utils/sign";
import { SUPPORTER_TASK_ID } from "../../config/constant";
import { isValidStakingKey } from "../../utils/taskState/stakingList";

// Helper function to verify request body
function verifyRequestBody(req: Request): {
  stakingKey: string;
} | null {
  try {
    console.log("Request body:", req.body);

    const stakingKey = req.body.stakingKey as string;
    if (!stakingKey) {
      return null;
    }
    return {  stakingKey };
  } catch {
    return null;
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
  const result = await StarFollowModel.findOne({
    stakingKey: requestBody.stakingKey,
    pendingRepos: { $ne: [] }
  });

  if (!result) {
    res.status(404).json({
      success: false,
      message: "No matching todo assignment found",
    });
    return;
  }

  res.status(200).json({
    success: true,
    message: "Todo assignment verified successfully",
    data: {
      githubUsername: result.gitHubUsername,
      pendingRepos: result.pendingRepos,
    }
  });
};


