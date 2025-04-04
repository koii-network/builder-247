import { Request, Response } from "express";
import { DocumentationModel } from "../../models/Documentation";
import { verifySignature } from "../../utils/sign";
import { documentSummarizerTaskID } from "../../config/constant";
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



async function checkToDoAssignment(
  stakingKey: string,
  roundNumber: string,
  githubUsername: string,
  prUrl: string,
): Promise<boolean> {
  try {
    const data = {
      stakingKey,
      roundNumber,
      githubUsername,
      prUrl,
      taskId: documentSummarizerTaskID,
    };
    console.log("Data:", data);

    const result = await DocumentationModel.findOneAndUpdate(
      {
        assignedTo: {
          $elemMatch: data,
        },
      }
    )
      .select("_id")
      .lean();

    console.log("Todo assignment check result:", result);
    return result !== null;
  } catch (error) {
    console.error("Error checking todo assignment:", error);
    return false;
  }
}

export const checkSummarizer = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }
  const isValid = await checkToDoAssignment(
    requestBody.stakingKey,
    requestBody.roundNumber,
    requestBody.githubUsername,
    requestBody.prUrl,
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


