import { Request, Response, NextFunction } from 'express';
import { v4 as uuidValidate } from 'uuid';

/**
 * Middleware to validate transaction ID in incoming requests
 * 
 * @param req Express request object
 * @param res Express response object
 * @param next Express next function
 */
export const transactionIdValidationMiddleware = (req: Request, res: Response, next: NextFunction) => {
  // Extract transaction ID from request headers or body
  const transactionId = req.headers['x-transaction-id'] || req.body?.transactionId;

  // Check if transaction ID is present
  if (!transactionId) {
    return res.status(400).json({
      error: 'Transaction ID is required',
      message: 'A valid transaction ID must be provided in the request headers (x-transaction-id) or body'
    });
  }

  // Validate transaction ID format (assuming UUID v4)
  if (typeof transactionId !== 'string' || !uuidValidate(transactionId)) {
    return res.status(400).json({
      error: 'Invalid Transaction ID',
      message: 'Transaction ID must be a valid UUID v4'
    });
  }

  // Attach validated transaction ID to request for downstream use
  req.transactionId = transactionId;

  // Proceed to next middleware/route handler
  next();
};