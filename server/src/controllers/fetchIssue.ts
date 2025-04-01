import { Request, response, Response } from "express";
import "dotenv/config";

import { TodoModel, TodoStatus } from "../models/Todo";
import { taskID } from "../constant";
import { isValidStakingKey } from "../utils/taskState";
import { IssueModel, IssueStatus } from "../models/Issue";
import { verifySignature } from "../utils/sign";
import { getPRDict } from "../utils/issueUtils";

// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string, roundNumber: number) {
  try {
    const result = await IssueModel.findOne({
      assignedStakingKey: stakingKey,
      assignedRoundNumber: roundNumber,
    })
      .select("title acceptanceCriteria repoOwner repoName issueUuid")
      .lean();

    if (!result) return null;

    return {
      issue: result,
      hasPR: Boolean(result.prUrl),
    };
  } catch (error) {
    console.error("Error checking assigned info:", error);
    return null;
  }
}
export function verifyRequestBody(req: Request): { signature: string; stakingKey: string; pubKey: string } | null {
  console.log("verifyRequestBody", req.body);
  try {
    const signature = req.body.signature as string;
    const stakingKey = req.body.stakingKey as string;
    const pubKey = req.body.pubKey as string;
    if (!signature || !stakingKey || !pubKey) {
      return null;
    }
    return { signature, stakingKey, pubKey };
  } catch {
    return null;
  }
}
async function verifySignatureData(
  signature: string,
  stakingKey: string,
  pubKey: string,
  action: string,
): Promise<{ roundNumber: number; githubUsername: string } | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log("bad signature");
      return null;
    }
    const body = JSON.parse(data);
    console.log({ signature_payload: body });
    if (
      !body.taskId ||
      typeof body.roundNumber !== "number" ||
      body.taskId !== taskID ||
      body.action !== action ||
      !body.githubUsername ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      console.log("bad signature data");
      return null;
    }
    return { roundNumber: body.roundNumber, githubUsername: body.githubUsername };
  } catch (error) {
    console.log("unexpected signature error", error);
    return null;
  }
}

export const fetchIssue = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(
    requestBody.signature,
    requestBody.stakingKey,
    requestBody.pubKey,
    "fetch_issue",
  );
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
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

  const existingAssignment = await checkExistingAssignment(requestBody.stakingKey, signatureData.roundNumber);

  if (existingAssignment) {
    if (existingAssignment.hasPR) {
      return {
        statuscode: 401,
        data: {
          success: false,
          message: "Issue already completed",
        },
      };
    }
    return {
      statuscode: 200,
      data: {
        success: true,
        data: existingAssignment.issue,
      },
    };
  }

  const fetchIssueLogic = async (
    requestBody: { signature: string; stakingKey: string; pubKey: string },
    signatureData: { roundNumber: number; githubUsername: string },
  ) => {
    try {
      const fifteenMinutesAgo = new Date(Date.now() - 15 * 60 * 1000);
      const eligibleIssue = await IssueModel.findOneAndUpdate(
        {
          $or: [
            { status: IssueStatus.ASSIGN_PENDING },
            {
              status: IssueStatus.IN_REVIEW,
              updatedAt: { $lt: fifteenMinutesAgo },
            },
          ],
        },
        {
          $set: {
            status: IssueStatus.IN_REVIEW,
            assignedStakingKey: requestBody.stakingKey,
            assignedGithubUsername: signatureData.githubUsername,
            assignedRoundNumber: signatureData.roundNumber,
            updatedAt: new Date(),
          },
        },
        { new: true, sort: { createdAt: 1 } },
      );

      if (!eligibleIssue) {
        return {
          statuscode: 404,
          data: {
            success: false,
            message: "No eligible issues found",
          },
        };
      }

      const prDict = await getPRDict(eligibleIssue.issueUuid);
      if (!prDict) {
        res.status(404).json({
          success: false,
          message: "Issue not found",
        });
        return;
      }

      return {
        statuscode: 200,
        data: {
          success: true,
          data: {
            repo_owner: eligibleIssue.repoOwner,
            repo_name: eligibleIssue.repoName,
            issue_uuid: eligibleIssue.issueUuid,
            pr_list: prDict,
          },
        },
      };
    } catch (error) {
      console.error("Error fetching issue:", error);
      return {
        statuscode: 500,
        data: {
          success: false,
          message: "Failed to fetch issue",
        },
      };
    }
  };
};
