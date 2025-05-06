import { Request, Response, NextFunction } from 'express';
import { verifySignature } from '../utils/sign';

/**
 * Middleware for validating cryptographic signatures of incoming requests
 * @param req Express request object
 * @param res Express response object
 * @param next Express next middleware function
 */
export const signatureValidationMiddleware = async (
  req: Request, 
  res: Response, 
  next: NextFunction
): Promise<void> => {
  try {
    // Extract signature from request headers or body
    const signature = req.headers['x-signature'] as string;
    const publicKey = req.headers['x-public-key'] as string;
    const payload = req.body;

    // Check if signature or public key is missing
    if (!signature || !publicKey) {
      res.status(400).json({
        error: 'Missing signature or public key',
        success: false
      });
      return;
    }

    // Validate signature
    const isValid = await verifySignature(
      JSON.stringify(payload), 
      publicKey, 
      signature
    );

    if (!isValid) {
      res.status(403).json({
        error: 'Invalid signature',
        success: false
      });
      return;
    }

    // If signature is valid, proceed to next middleware
    next();
  } catch (error) {
    console.error('Signature validation error:', error);
    res.status(500).json({
      error: 'Internal server error during signature validation',
      success: false
    });
  }
};