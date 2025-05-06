import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';

/**
 * Signature validation middleware to verify request signatures
 * @param req Express request object
 * @param res Express response object
 * @param next Next middleware function
 */
export const signatureValidationMiddleware = (
  req: Request, 
  res: Response, 
  next: NextFunction
) => {
  try {
    // Extract signature from request headers
    const signature = req.headers['x-signature'] as string;
    const publicKey = req.headers['x-public-key'] as string;

    // Check if signature and public key are present
    if (!signature || !publicKey) {
      return res.status(400).json({ 
        error: 'Missing signature or public key' 
      });
    }

    // Convert request body to a string for verification
    const bodyString = JSON.stringify(req.body);

    // Verify the signature
    const verifier = crypto.createVerify('SHA256');
    verifier.update(bodyString);

    const isValid = verifier.verify(
      publicKey, 
      Buffer.from(signature, 'base64')
    );

    // If signature is not valid, return an error
    if (!isValid) {
      return res.status(403).json({ 
        error: 'Invalid signature' 
      });
    }

    // If signature is valid, proceed to next middleware
    next();
  } catch (error) {
    console.error('Signature validation error:', error);
    res.status(500).json({ 
      error: 'Internal server error during signature validation' 
    });
  }
};