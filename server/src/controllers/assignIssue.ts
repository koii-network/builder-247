import { Request, Response } from "express";
import { IssueModel, IssueStatus } from "../models/Issue";
import { taskIDs } from "../constant";

export function verifyRequestBody(req: Request): string | null {
  console.log("verifyRequestBody", req.body);
  const taskId = req.body.taskId as string;
  if (!taskId || !taskIDs.includes(taskId)) {
    return null;
  }
  return taskId;
}

export const assignIssue = async (req: Request, res: Response) => {
  const taskId = verifyRequestBody(req);
  if (!taskId) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const response = await assignIssueLogic(taskId);
  res.status(response.statuscode).json(response.data);
};

export const assignIssueLogic = async (taskId: string) => {
  const fiveMinutesAgo = new Date(Date.now() - 300000); // 5 minutes in milliseconds

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

  await IssueModel.findByIdAndUpdate(
    result.nextIssue._id,
    {
      $set: { status: IssueStatus.AGGREGATOR_PENDING },
    },
    { new: true },
  );

  return {
    statuscode: 200,
    data: {
      success: true,
      message: "Issue assigned",
      issueId: result.nextIssue.issueUuid,
      repoOwner: result.nextIssue.repoOwner,
      repoName: result.nextIssue.repoName,
    },
  };
};
