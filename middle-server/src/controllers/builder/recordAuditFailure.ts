import { Request, Response } from 'express';
import { TodoModel, TodoStatus } from '../../models/Todo';
import { IssueModel, IssueStatus } from '../../models/Issue';
import { verifySignature } from '../../utils/sign';
import { taskIDs } from '../../config/constant';

interface RecordAuditFailureRequest {
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
  submissionSignature: string; // Signature from the original submission
  isRecoverable: boolean; // Whether this is a recoverable failure
}

export const recordAuditFailure = async (req: Request, res: Response): Promise<void> => {
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
      submissionSignature,
      isRecoverable,
    } = req.body as RecordAuditFailureRequest;

    // Verify the audit signature
    const { data: auditData, error: auditError } = await verifySignature(signature, stakingKey);
    if (auditError || !auditData) {
      res.status(401).json({
        success: false,
        message: 'Invalid audit signature',
      });
      return;
    }

    // Parse and validate audit signature data
    try {
      const body = JSON.parse(auditData);
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
          message: 'Invalid audit signature payload',
        });
        return;
      }
    } catch (error) {
      console.error('Error parsing audit signature data:', error);
      res.status(401).json({
        success: false,
        message: 'Invalid audit signature data format',
      });
      return;
    }

    // Verify the submission signature to ensure we're failing the right work
    const { data: submissionData, error: submissionError } = await verifySignature(
      submissionSignature,
      stakingKey
    );
    if (submissionError || !submissionData) {
      res.status(401).json({
        success: false,
        message: 'Invalid submission signature',
      });
      return;
    }

    // Parse and validate submission signature data
    try {
      const body = JSON.parse(submissionData);
      if (
        !body.taskId ||
        typeof body.roundNumber !== 'number' ||
        !taskIDs.includes(body.taskId) ||
        body.taskId !== taskId ||
        body.roundNumber !== roundNumber ||
        !body.action ||
        body.action !== 'audit'
      ) {
        res.status(401).json({
          success: false,
          message: 'Invalid submission signature payload',
        });
        return;
      }
    } catch (error) {
      console.error('Error parsing submission signature data:', error);
      res.status(401).json({
        success: false,
        message: 'Invalid submission signature data format',
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
            status: TodoStatus.INITIALIZED, // Reset status
            'assignees.$.failedReason': failureReason,
            'assignees.$.failedFeedback': failureFeedback,
            'assignees.$.recoverableFailure': isRecoverable,
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
            status: IssueStatus.ASSIGN_PENDING, // Reset status
            'assignees.$.failedAuditReason': failureReason,
            'assignees.$.failedAuditFeedback': failureFeedback,
            'assignees.$.recoverableFailure': isRecoverable,
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
      message: 'Audit failure recorded successfully',
    });
  } catch (error) {
    console.error('Error recording audit failure:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while recording audit failure',
    });
  }
};
