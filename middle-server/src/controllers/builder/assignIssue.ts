import { Request, Response } from "express";
import { IssueModel, IssueStatus } from "../../models/Issue";
import { taskIDs } from "../../config/constant";

export function verifyRequestBody(req: Request): { taskId: string; githubUsername: string } | null {
  console.log("verifyRequestBody", req.body);
  const taskId = req.body.taskId as string;
  const githubUsername = req.body.githubUsername as string;
  if (!taskId || !taskIDs.includes(taskId) || !githubUsername) {
    return null;
  }
  return { taskId, githubUsername };
}

export const assignIssue = async (req: Request, res: Response) => {
  const body = verifyRequestBody(req);
  if (!body) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const { taskId, githubUsername } = body;

  const response = await assignIssueLogic(taskId, githubUsername);
  res.status(response.statuscode).json(response.data);
};

export const assignIssueLogic = async (taskId: string, githubUsername: string) => {
  // Find the next issue to assign
  const result = await IssueModel.findOneAndUpdate(
    {
      status: IssueStatus.INITIALIZED,
    },
    {
      $push: {
        assignees: {
          githubUsername: githubUsername,
          roundNumber: 0, // Initial round number
        },
      },
      $set: {
        status: IssueStatus.AGGREGATOR_PENDING,
      },
    },
    { new: true },
  );

  if (!result) {
    return {
      statuscode: 409,
      data: {
        success: false,
        message: "No issues available for assignment",
      },
    };
  }

  const data = {
    success: true,
    message: "Issue assigned",
    issueId: result.issueUuid,
    repoOwner: result.repoOwner,
    repoName: result.repoName,
  };

  console.log("data", data);

  return {
    statuscode: 200,
    data,
  };
};
