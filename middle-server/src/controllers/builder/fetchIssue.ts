import { Request, Response } from 'express';
import 'dotenv/config';

import { taskIDs } from '../../config/constant';
import { isValidStakingKey } from '../../utils/taskState/stakingList';
import { IssueModel, IssueStatus } from '../../models/Issue';
import { verifySignature } from '../../utils/sign';
import { getPRDict } from '../../utils/issueUtils';

// Check if the user has already completed the task
async function checkExistingAssignment(stakingKey: string, roundNumber: number) {
  try {
    console.log(
      `Checking existing assignment for stakingKey: ${stakingKey}, round: ${roundNumber}`
    );
    const result = await IssueModel.findOne({
      assignees: {
        $elemMatch: {
          stakingKey: stakingKey,
          roundNumber: roundNumber,
        },
      },
    })
      .select('title acceptanceCriteria repoName uuid assignees aggregatorOwner status')
      .lean();

    console.log('Existing assignment query result:', {
      found: !!result,
      uuid: result?.uuid,
      status: result?.status,
      assigneesCount: result?.assignees?.length,
      assignees: result?.assignees,
    });

    if (!result) return null;

    const hasPR = Boolean(result.assignees?.find((a) => a.prUrl));
    console.log(`Has PR: ${hasPR}`);

    return {
      issue: result,
      hasPR,
    };
  } catch (error) {
    console.error('Error checking assigned info:', error);
    return null;
  }
}
export function verifyRequestBody(
  req: Request
): { signature: string; stakingKey: string; pubKey: string } | null {
  console.log('verifyRequestBody', req.body);
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
  action: string
): Promise<{ roundNumber: number; githubUsername: string; taskId: string } | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log('bad signature');
      return null;
    }
    const body = JSON.parse(data);
    console.log({ signature_payload: body });
    if (
      !body.taskId ||
      typeof body.roundNumber !== 'number' ||
      !taskIDs.includes(body.taskId) ||
      body.action !== action ||
      !body.githubUsername ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey
    ) {
      console.log('bad signature data');
      return null;
    }
    return {
      roundNumber: body.roundNumber,
      githubUsername: body.githubUsername,
      taskId: body.taskId,
    };
  } catch (error) {
    console.log('unexpected signature error', error);
    return null;
  }
}

export const fetchIssue = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: 'Invalid request body',
    });
    return;
  }

  const signatureData = await verifySignatureData(
    requestBody.signature,
    requestBody.stakingKey,
    requestBody.pubKey,
    'fetch-issue'
  );
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: 'Failed to verify signature',
    });
    return;
  }

  if (!(await isValidStakingKey(requestBody.stakingKey, signatureData.taskId))) {
    res.status(401).json({
      success: false,
      message: 'Invalid staking key',
    });
    return;
  }

  const response = await fetchIssueLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);
};

export const fetchIssueLogic = async (
  requestBody: { signature: string; stakingKey: string; pubKey: string },
  signatureData: { roundNumber: number; githubUsername: string; taskId: string }
) => {
  console.log('Starting fetchIssueLogic with:', {
    stakingKey: requestBody.stakingKey,
    roundNumber: signatureData.roundNumber,
    githubUsername: signatureData.githubUsername,
  });

  // 1. Check if user already has an assignment
  const existingAssignment = await checkExistingAssignment(
    requestBody.stakingKey,
    signatureData.roundNumber
  );

  if (existingAssignment) {
    console.log('Found existing assignment:', {
      uuid: existingAssignment.issue.uuid,
      status: existingAssignment.issue.status,
      hasPR: existingAssignment.hasPR,
    });

    if (existingAssignment.hasPR) {
      return {
        statuscode: 409,
        data: {
          success: false,
          message: 'Issue already completed',
        },
      };
    }

    console.log('existingAssignment', existingAssignment);

    // Get PR dict for the existing assignment
    const prDict = await getPRDict(existingAssignment.issue.uuid);
    console.log('PR dict for existing assignment:', prDict);

    // Return consistent response format with snake_case
    return {
      statuscode: 200,
      data: {
        success: true,
        data: {
          // Use aggregatorOwner if it exists, otherwise fallback to repoOwner
          repo_owner: existingAssignment.issue.aggregatorOwner,
          repo_name: existingAssignment.issue.repoName,
          issue_uuid: existingAssignment.issue.uuid,
          pr_list: prDict || {},
        },
      },
    };
  }

  try {
    console.log('Looking for eligible issue with status:', IssueStatus.ASSIGN_PENDING);

    // First check what issues are available
    const availableIssues = await IssueModel.find({
      status: IssueStatus.ASSIGN_PENDING,
    })
      .select('uuid status')
      .lean();

    console.log('Available issues before assignment:', availableIssues);

    const eligibleIssue = await IssueModel.findOneAndUpdate(
      { status: IssueStatus.ASSIGN_PENDING },
      {
        $set: {
          status: IssueStatus.ASSIGNED,
          updatedAt: new Date(),
        },
        $push: {
          assignees: {
            stakingKey: requestBody.stakingKey,
            githubUsername: signatureData.githubUsername,
            roundNumber: signatureData.roundNumber,
          },
        },
      },
      { new: true, sort: { createdAt: 1 } }
    );

    console.log('Eligible issue found:', {
      found: !!eligibleIssue,
      uuid: eligibleIssue?.uuid,
      status: eligibleIssue?.status,
      assigneesCount: eligibleIssue?.assignees?.length,
    });

    if (!eligibleIssue) {
      return {
        statuscode: 409,
        data: {
          success: false,
          message: 'No eligible issues found',
        },
      };
    }

    const prDict = await getPRDict(eligibleIssue.uuid);
    if (!prDict) {
      return {
        statuscode: 409,
        data: {
          success: false,
          message: 'Issue not found',
        },
      };
    }

    return {
      statuscode: 200,
      data: {
        success: true,
        data: {
          repo_owner: eligibleIssue.aggregatorOwner,
          repo_name: eligibleIssue.repoName,
          issue_uuid: eligibleIssue.uuid,
          pr_list: prDict,
        },
      },
    };
  } catch (error) {
    console.error('Error fetching issue:', error);
    return {
      statuscode: 500,
      data: {
        success: false,
        message: 'Failed to fetch issue',
      },
    };
  }
};
