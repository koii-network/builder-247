import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

/**
 * Middleware for validating and processing transaction IDs
 * 
 * @param req Express request object
 * @param res Express response object
 * @param next Express next function
 */
export const transactionIdValidation = (req: Request, res: Response, next: NextFunction) => {
  // Extract transaction ID from request headers or body
  const transactionId = 
    req.headers['x-transaction-id'] as string || 
    req.body?.transactionId || 
    req.query?.transactionId as string;

  // If no transaction ID is provided, generate a new UUID
  if (!transactionId) {
    req.transactionId = uuidv4();
    return next();
  }

  // Validate transaction ID format (must be a valid UUID)
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  
  if (!uuidRegex.test(transactionId)) {
    return res.status(400).json({
      error: 'Invalid transaction ID format',
      message: 'Transaction ID must be a valid UUID'
    });
  }

  // Attach validated transaction ID to the request
  req.transactionId = transactionId;

  next();
};

// Extend Request interface to include transactionId
declare global {
  namespace Express {
    interface Request {
      transactionId?: string;
    }
  }
}