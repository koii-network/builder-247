import { Request, Response, NextFunction } from 'express';
import { v4 as uuidValidate } from 'uuid';

/**
 * Middleware to validate Transaction ID in incoming requests
 * @param req Express request object
 * @param res Express response object
 * @param next Express next function
 */
export const transactionIdValidator = (req: Request, res: Response, next: NextFunction) => {
  const transactionId = req.headers['x-transaction-id'] as string | undefined;

  // Check if transaction ID is present
  if (!transactionId) {
    return res.status(400).json({
      error: 'Transaction ID is required',
      message: 'Every request must include a valid transaction ID in x-transaction-id header'
    });
  }

  // Validate Transaction ID as UUID v4
  if (!uuidValidate(transactionId)) {
    return res.status(400).json({
      error: 'Invalid Transaction ID',
      message: 'Transaction ID must be a valid UUID v4'
    });
  }

  // Optional: Attach transaction ID to request for downstream use
  (req as any).transactionId = transactionId;

  next();
};