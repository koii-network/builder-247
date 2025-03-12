import { Request, Response } from "express";
import { TodoModel } from "../models/Todo";
import { isValidStakingKey } from "../utils/taskState";
import { taskID } from "../constant";

// Helper function to verify request body
function verifyRequestBody(req: Request): {
  stakingKey: string;
  pubKey: string;
  roundNumber: number;
  githubUsername: string;
  prUrl: string;
  taskId: string;
} | null {
  try {
    console.log("Request body:", req.body);
    const stakingKey = req.body.stakingKey as string;
    const pubKey = req.body.pubKey as string;
    const roundNumber = req.body.roundNumber as number;
    const githubUsername = req.body.githubUsername as string;
    const prUrl = req.body.prUrl as string;
    const taskId = req.body.taskId as string;

    if (!stakingKey || !pubKey || !roundNumber || !githubUsername || !prUrl || !taskId) {
      return null;
    }
    return { stakingKey, pubKey, roundNumber, githubUsername, prUrl, taskId };
  } catch {
    return null;
  }
}

async function checkToDoAssignment(
  stakingKey: string,
  roundNumber: number,
  githubUsername: string,
  prUrl: string,
): Promise<boolean> {
  try {
    const data = {
      stakingKey,
      roundNumber,
      githubUsername,
      prUrl,
      taskId: taskID,
    };
    console.log("Checking todo assignment with data:", data);

    const result = await TodoModel.findOne({
      assignedTo: {
        $elemMatch: data,
      },
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
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  if (requestBody.taskId !== taskID) {
    res.status(401).json({
      success: false,
      message: "Invalid task ID",
    });
    return;
  }

  if (!(await isValidStakingKey(requestBody.stakingKey))) {
    res.status(401).json({
      success: false,
      message: "Invalid staking key",
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
