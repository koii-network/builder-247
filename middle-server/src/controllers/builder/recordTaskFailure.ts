import { Request, Response } from 'express';
import { TodoModel } from '../../models/Todo';
import { IssueModel } from '../../models/Issue';
import { verifySignature } from '../../utils/sign';
import { taskIDs } from '../../config/constant';

interface RecordFailureRequest {
  taskId: string;
  stakingKey: string;
  signature: string;
  pubKey: string;
  failureReason: string;
  failureFeedback: string;
  roundNumber: number;
  nodeType: 'worker' | 'leader';
  todoUuid?: string;
  issueUuid?: string;
}

export const recordTaskFailure = async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      taskId,
      stakingKey,
      signature,
      pubKey,
      failureReason,
      failureFeedback,
      roundNumber,
      nodeType,
      todoUuid,
      issueUuid,
    } = req.body as RecordFailureRequest;

    // Verify the signature
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      res.status(401).json({
        success: false,
        message: 'Invalid signature',
      });
      return;
    }

    // Parse and validate signature data
    try {
      const body = JSON.parse(data);
      if (
        !body.taskId ||
        typeof body.roundNumber !== 'number' ||
        !taskIDs.includes(body.taskId) ||
        !body.pubKey ||
        body.pubKey !== pubKey ||
        !body.stakingKey ||
        body.stakingKey !== stakingKey ||
        body.taskId !== taskId ||
        body.roundNumber !== roundNumber
      ) {
        res.status(401).json({
          success: false,
          message: 'Invalid signature payload',
        });
        return;
      }
    } catch (error) {
      console.error('Error parsing signature data:', error);
      res.status(401).json({
        success: false,
        message: 'Invalid signature data format',
      });
      return;
    }

    // Update the appropriate model based on node type
    if (nodeType === 'worker' && todoUuid) {
      // Update Todo model - find and update in one operation
      const todo = await TodoModel.findOneAndUpdate(
        {
          uuid: todoUuid,
          assignees: {
            $elemMatch: {
              stakingKey,
              roundNumber,
            },
          },
        },
        {
          $set: {
            'assignees.$.failedReason': failureReason,
            'assignees.$.failedFeedback': failureFeedback,
          },
        },
        { new: true }
      );

      if (!todo) {
        res.status(403).json({
          success: false,
          message: 'Not authorized - user is not an assignee for this todo',
        });
        return;
      }
    } else if (nodeType === 'leader' && issueUuid) {
      // Update Issue model - find and update in one operation
      const issue = await IssueModel.findOneAndUpdate(
        {
          issueUuid,
          assignees: {
            $elemMatch: {
              stakingKey,
              roundNumber,
            },
          },
        },
        {
          $set: {
            'assignees.$.failedAuditReason': failureReason,
            'assignees.$.failedAuditFeedback': failureFeedback,
          },
        },
        { new: true }
      );

      if (!issue) {
        res.status(403).json({
          success: false,
          message: 'Not authorized - user is not an assignee for this issue',
        });
        return;
      }
    } else {
      res.status(400).json({
        success: false,
        message: 'Invalid node type or missing UUID',
      });
      return;
    }

    res.json({
      success: true,
      message: 'Task failure recorded successfully',
    });
  } catch (error) {
    console.error('Error recording task failure:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while recording task failure',
    });
  }
};
