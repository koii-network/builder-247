import { Request, Response } from "express";
import { IssueModel, IssueStatus } from "../models/Issue";
import { taskIDs } from "../constant";

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
  const fiveMinutesAgo = new Date(Date.now() - 300000);

  const [result] = await IssueModel.aggregate([
    {
      $facet: {
        activeCheck: [
          {
            $match: {
              taskId,
            },
          },
          {
            $match: {
              $or: [
                { status: IssueStatus.IN_PROCESS },
                {
                  $and: [{ status: IssueStatus.AGGREGATOR_PENDING }, { updatedAt: { $gt: fiveMinutesAgo } }],
                },
              ],
            },
          },
          { $limit: 1 },
        ],
        nextIssue: [
          {
            $match: {
              $or: [
                { status: IssueStatus.INITIALIZED },
                {
                  $and: [{ status: IssueStatus.AGGREGATOR_PENDING }, { updatedAt: { $lt: fiveMinutesAgo } }],
                },
              ],
            },
          },
          { $sort: { createdAt: 1 } },
          { $limit: 1 },
        ],
      },
    },
    {
      $project: {
        hasActive: { $gt: [{ $size: "$activeCheck" }, 0] },
        nextIssue: { $arrayElemAt: ["$nextIssue", 0] },
      },
    },
  ]);

  if (result.hasActive) {
    return {
      statuscode: 400,
      data: {
        success: false,
        message: "Issue is already in process",
      },
    };
  }
  if (!result.nextIssue) {
    return {
      statuscode: 404,
      data: {
        success: false,
        message: "No issue found",
      },
    };
  }

  if (githubUsername === result.nextIssue.repoOwner) {
    return {
      statuscode: 400,
      data: {
        success: false,
        message: "Aggregator cannot be the same as the repo owner",
      },
    };
  }
  await IssueModel.findByIdAndUpdate(
    result.nextIssue._id,
    {
      $set: { status: IssueStatus.AGGREGATOR_PENDING },
    },
    { new: true },
  );

  const data = {
    success: true,
    message: "Issue assigned",
    issueId: result.nextIssue.issueUuid,
    repoOwner: result.nextIssue.repoOwner,
    repoName: result.nextIssue.repoName,
  };

  console.log("data", data);

  return {
    statuscode: 200,
    data,
  };
};
