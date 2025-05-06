import { Request, Response, NextFunction } from 'express';
import { verifySignature } from '../utils/sign';

/**
 * Middleware for validating digital signatures of incoming requests
 * Checks the integrity and authenticity of the request payload
 */
export const signatureValidationMiddleware = (req: Request, res: Response, next: NextFunction) => {
  try {
    const { signature, data } = req.body;

    // Signature is required for validation
    if (!signature || !data) {
      return res.status(400).json({
        error: 'Signature and data are required for validation',
        success: false
      });
    }

    // Verify the signature using the utility function
    const isValid = verifySignature(data, signature);

    if (!isValid) {
      return res.status(403).json({
        error: 'Invalid signature: Request authenticity could not be verified',
        success: false
      });
    }

    // If signature is valid, proceed to the next middleware/route handler
    next();
  } catch (error) {
    console.error('Signature validation error:', error);
    res.status(500).json({
      error: 'Internal server error during signature validation',
      success: false
    });
  }
};