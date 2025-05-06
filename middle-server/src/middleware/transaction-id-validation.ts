import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

/**
 * Validates and ensures the presence of a valid Transaction ID
 * 
 * @param req Express request object
 * @param res Express response object
 * @param next Express next middleware function
 */
export const validateTransactionId = (req: Request, res: Response, next: NextFunction) => {
  // Extract transaction ID from headers or body
  const transactionId = 
    req.headers['x-transaction-id'] as string || 
    req.body?.transactionId || 
    req.query?.transactionId as string;

  // If no transaction ID is provided, generate a new one
  if (!transactionId) {
    req.transactionId = uuidv4();
    return next();
  }

  // Validate Transaction ID format (UUID v4)
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  
  if (!uuidRegex.test(transactionId)) {
    return res.status(400).json({
      error: 'Invalid Transaction ID',
      message: 'Transaction ID must be a valid UUID v4'
    });
  }

  // Attach transaction ID to request for downstream use
  req.transactionId = transactionId;
  
  next();
};

// Extend the Express Request interface to include transactionId
declare global {
  namespace Express {
    interface Request {
      transactionId?: string;
    }
  }
}