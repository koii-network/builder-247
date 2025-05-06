import { Request, Response, NextFunction } from 'express';
import { verifySignature } from '../utils/sign';

export interface SignedRequest extends Request {
  validatedData?: string;
}

export async function validateSignature(req: SignedRequest, res: Response, next: NextFunction) {
  try {
    // Check if signature headers are present
    const signature = req.headers['x-signature'] as string;
    const stakingKey = req.headers['x-staking-key'] as string;

    if (!signature || !stakingKey) {
      return res.status(400).json({ error: 'Missing signature or staking key' });
    }

    // Verify signature
    const verificationResult = await verifySignature(signature, stakingKey);

    if (verificationResult.error) {
      return res.status(401).json({ error: verificationResult.error });
    }

    // If verification succeeds, attach validated data to request
    req.validatedData = verificationResult.data ? JSON.parse(verificationResult.data) : undefined;
    next();
  } catch (error) {
    console.error('Signature validation error:', error);
    res.status(500).json({ error: 'Internal server error during signature validation' });
  }
}