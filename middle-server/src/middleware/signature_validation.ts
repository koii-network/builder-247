import { Request, Response, NextFunction } from 'express';
import { verifySignature } from '../utils/sign';

interface SignedRequest extends Request {
  verifiedData?: any;
}

export async function validateSignature(req: SignedRequest, res: Response, next: NextFunction) {
  try {
    // Check if signature is present in headers
    const signature = req.headers['x-signature'] as string;
    const stakingKey = req.headers['x-staking-key'] as string;

    if (!signature || !stakingKey) {
      return res.status(400).json({ 
        error: 'Missing signature or staking key', 
        message: 'Signature validation requires x-signature and x-staking-key headers' 
      });
    }

    // Parse the request body 
    const bodyToVerify = req.body;

    // Verify the signature
    const verificationResult = await verifySignature(signature, stakingKey);

    if (verificationResult.error) {
      return res.status(401).json({ 
        error: 'Signature verification failed', 
        details: verificationResult.error 
      });
    }

    // If verification succeeds, attach verified data to request
    req.verifiedData = JSON.parse(verificationResult.data || '{}');
    next();

  } catch (error) {
    console.error('Signature validation middleware error:', error);
    res.status(500).json({ 
      error: 'Internal server error during signature validation', 
      message: error instanceof Error ? error.message : 'Unknown error' 
    });
  }
}