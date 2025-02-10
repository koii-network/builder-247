import { Request, Response } from "express";
import { TodoModel, TodoStatus } from "../models/Todo";
import { verifySignature } from "../utils/sign";
import { taskID } from "../constant";
// TODO: The high concurrent situation there might be some issues, need to be optimized
import { isValidStakingKey } from "../utils/taskState";
// Helper function to verify request body
function verifyRequestBody(req: Request): { signature: string; pubKey: string; github_username: string } | null {
  try {
    console.log("Body:", req.body);
    const signature = req.body.signature as string;
    const pubKey = req.body.pubKey as string;
    const github_username = req.body.github_username as string;
    if (!signature || !pubKey || !github_username) {
      return null;
    }
    return { signature, pubKey, github_username };
  } catch {
    return null;
  }
}

// Helper function to verify signature
async function verifySignatureData(signature: string, pubKey: string): Promise<{ roundNumber: number } | null> {
  try {
    const { data, error } = await verifySignature(signature, pubKey);
    console.log("Decoded Data:", data);
    console.log("Decoded Error:", error);
    if (error || !data) {
      return null;
    }
    const body = JSON.parse(data);
    console.log("Decoded JSON Body:", body);
    console.log(body.taskId, taskID);
    console.log(body.roundNumber);
    if (!body.taskId || !body.roundNumber || body.taskId !== taskID) {
      return null;
    }
    return { roundNumber: body.roundNumber };
  } catch {
    return null;
  }
}

async function checkAssignedInfoExists(stakingKey: string, roundNumber: number): Promise<boolean> {
  try {
    const result = await TodoModel.findOne({
      "assignedTo.stakingKey": stakingKey,
      "assignedTo.roundNumber": roundNumber,
    })
      .select("_id")
      .lean();
    console.log("findone result", result);
    return result !== null;
  } catch (error) {
    console.error("Error checking assigned info:", error);
    return false;
  }
}

export const fetchTodo = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(requestBody.signature, requestBody.pubKey);
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  if (!(await isValidStakingKey(requestBody.pubKey))) {
    res.status(401).json({
      success: false,
      message: "Invalid staking key",
    });
    return;
  }
  console.log();
  if (await checkAssignedInfoExists(requestBody.pubKey, signatureData.roundNumber)) {
    res.status(401).json({
      success: false,
      message: "Assigned info already exists for this round",
    });
    return;
  }

  try {
    const todos = await TodoModel.find({
      status: TodoStatus.INITIALIZED,
      $expr: { $lt: [{ $size: "$assignedTo" }, 2] },
    }).sort({ createdAt: 1 });

    if (todos.length === 0) {
      res.status(404).json({
        success: false,
        message: "No todos available",
      });
      return;
    }
    console.log("todos listed", todos);
    const updatedTodo = await TodoModel.findOneAndUpdate(
      {
        _id: todos[0]?._id,
        $expr: { $lt: [{ $size: "$assignedTo" }, 2] },
      },
      {
        $push: {
          assignedTo: {
            stakingKey: requestBody.pubKey,
            taskId: taskID,
            roundNumber: signatureData.roundNumber,
            githubUsername: requestBody.github_username,
          },
        },
      },
      { new: true },
    );

    if (!updatedTodo) {
      res.status(409).json({
        success: false,
        message: "Task assignment conflict",
      });
      return;
    }

    res.status(200).json({
      success: true,
      data: {
        title: updatedTodo.title,
        acceptance_criteria: updatedTodo.acceptanceCriteria,
        repo_owner: updatedTodo.repoOwner,
        repo_name: updatedTodo.repoName,
      },
    });
  } catch (error) {
    console.error("Error fetching todos:", error);
    res.status(500).json({
      success: false,
      message: "Failed to fetch todos",
    });
  }
};
