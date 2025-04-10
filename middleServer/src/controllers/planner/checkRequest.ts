import { Request, Response } from "express";
import { Spec, SpecModel } from "../../models/Spec";
import { verifySignature } from "../../utils/sign";
import { plannerTaskID } from "../../config/constant";
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
): Promise<Spec | null> {
  try {
    const data = {
      stakingKey,
      roundNumber,
      githubUsername,
      prUrl,
      taskId: plannerTaskID,
    };
    console.log("Data:", data);

    const result = await SpecModel.findOne(
      {
        "assignedTo": {
          $elemMatch: {
            stakingKey: stakingKey,
            taskId: plannerTaskID,
            roundNumber: Number(roundNumber),
          }
        }
      }
    )

    console.log("Todo assignment check result:", result);
    return result;
  } catch (error) {
    console.error("Error checking todo assignment:", error);
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
  const spec = await checkToDoAssignment(
    requestBody.stakingKey,
    requestBody.roundNumber,
    requestBody.githubUsername,
    requestBody.prUrl,
  );

  if (!spec) {
    res.status(404).json({
      success: false,
      message: "No matching todo assignment found",
    });
    return;
  }

  res.status(200).json({
    success: true,
    message: "Todo assignment verified successfully",
    data:{
      ...spec
    }
  });
};


// export const test = async () => {
//   const response = await checkToDoAssignment("0x123", "1", "", "0x123");
//   console.log(response);
// }

// test();
