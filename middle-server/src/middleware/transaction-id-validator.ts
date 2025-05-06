import { Request, Response, NextFunction } from 'express';
import { v4 as uuidValidate } from 'uuid';
import { performance } from 'perf_hooks';
import { Logger } from '../utils/logging'; // Assuming a centralized logging utility

// In-memory cache for tracking unique transaction IDs (for demonstration)
// In a production scenario, replace with a distributed cache like Redis
const TRANSACTION_CACHE = new Set<string>();
const MAX_CACHE_SIZE = 10000;

interface TransactionValidationError {
  error: string;
  message: string;
  transactionId?: string;
}

/**
 * Middleware to validate Transaction ID in incoming requests
 * @param req Express request object
 * @param res Express response object
 * @param next Express next function
 */
export const transactionIdValidator = (req: Request, res: Response, next: NextFunction) => {
  const startTime = performance.now();
  const transactionId = req.headers['x-transaction-id'] as string | undefined;
  const clientIp = req.ip || 'unknown';

  const logRejection = (error: TransactionValidationError) => {
    Logger.warn('Transaction ID Validation Failed', {
      transactionId: error.transactionId,
      clientIp,
      error: error.error
    });
  };

  // Check if transaction ID is present
  if (!transactionId) {
    const error: TransactionValidationError = {
      error: 'Transaction ID is required',
      message: 'Every request must include a valid transaction ID in x-transaction-id header'
    };
    logRejection(error);
    return res.status(400).json(error);
  }

  // Validate Transaction ID as UUID v4
  if (!uuidValidate(transactionId)) {
    const error: TransactionValidationError = {
      error: 'Invalid Transaction ID',
      message: 'Transaction ID must be a valid UUID v4',
      transactionId
    };
    logRejection(error);
    return res.status(400).json(error);
  }

  // Check transaction ID uniqueness
  if (TRANSACTION_CACHE.has(transactionId)) {
    const error: TransactionValidationError = {
      error: 'Duplicate Transaction ID',
      message: 'This transaction ID has already been processed',
      transactionId
    };
    logRejection(error);
    return res.status(409).json(error);
  }

  // Add transaction ID to cache
  TRANSACTION_CACHE.add(transactionId);
  if (TRANSACTION_CACHE.size > MAX_CACHE_SIZE) {
    // Remove oldest entry if cache exceeds max size
    const oldestTransactionId = TRANSACTION_CACHE.values().next().value;
    TRANSACTION_CACHE.delete(oldestTransactionId);
  }

  // Attach transaction ID to request for downstream use
  (req as any).transactionId = transactionId;

  // Log successful validation
  const endTime = performance.now();
  const validationLatency = endTime - startTime;
  
  Logger.info('Transaction ID Validated', {
    transactionId,
    clientIp,
    latencyMs: validationLatency
  });

  // Ensure middleware doesn't exceed 100ms
  if (validationLatency > 100) {
    Logger.warn('Transaction ID Validation Exceeded Latency Threshold', {
      transactionId,
      latencyMs: validationLatency
    });
  }

  next();
};