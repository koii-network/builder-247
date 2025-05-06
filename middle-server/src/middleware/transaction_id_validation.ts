import { Request, Response, NextFunction } from 'express';
import { v4 as uuidValidate } from 'uuid';

/**
 * Middleware to validate transaction ID
 * 
 * Validates that:
 * 1. Transaction ID is present
 * 2. Transaction ID is a valid UUID v4
 * 3. Transaction ID is not an empty string
 */
export const validateTransactionId = (req: Request, res: Response, next: NextFunction) => {
  const transactionId = req.headers['x-transaction-id'] as string;

  // Check if transaction ID is missing
  if (!transactionId) {
    return res.status(400).json({
      error: 'Transaction ID is required',
      message: 'A valid transaction ID must be provided in the x-transaction-id header'
    });
  }

  // Trim whitespace
  const trimmedTransactionId = transactionId.trim();

  // Check if transaction ID is an empty string after trimming
  if (trimmedTransactionId.length === 0) {
    return res.status(400).json({
      error: 'Invalid Transaction ID',
      message: 'Transaction ID cannot be an empty string'
    });
  }

  // Validate UUID v4 format
  if (!uuidValidate(trimmedTransactionId)) {
    return res.status(400).json({
      error: 'Invalid Transaction ID',
      message: 'Transaction ID must be a valid UUID v4'
    });
  }

  // If validation passes, attach the validated transaction ID to the request
  req.validatedTransactionId = trimmedTransactionId;
  
  next();
};

// Extend the Request interface to include the validated transaction ID
declare global {
  namespace Express {
    interface Request {
      validatedTransactionId?: string;
    }
  }
}