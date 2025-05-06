import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

// In-memory store of nonces to prevent replay attacks
const usedNonces = new Set<string>();
const NONCE_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes

export const verifyBearerToken = (req: Request, res: Response, next: NextFunction): void => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader) {
    res.status(401).json({ 
      success: false,
      message: 'No authorization header provided' 
    });
    return;
  }

  const token = authHeader.split(' ')[1];
  
  if (!token) {
    res.status(401).json({ 
      success: false,
      message: 'No bearer token provided' 
    });
    return;
  }

  // Check bearer token
  const expectedToken = process.env.PROMETHEUS_INCOME_REQUEST_API_KEY;
  
  if (token !== expectedToken) {
    res.status(403).json({ 
      success: false,
      message: 'Invalid bearer token' 
    });
    return;
  }

  next();
};

export const preventReplayAttack = (req: Request, res: Response, next: NextFunction): void => {
  const nonce = req.headers['x-request-nonce'] as string;
  const timestamp = req.headers['x-request-timestamp'] as string;

  // Validate nonce exists
  if (!nonce) {
    res.status(400).json({
      success: false,
      message: 'Request nonce is required'
    });
    return;
  }

  // Validate timestamp
  const requestTime = parseInt(timestamp, 10);
  if (isNaN(requestTime)) {
    res.status(400).json({
      success: false,
      message: 'Invalid request timestamp'
    });
    return;
  }

  // Check if nonce has been used recently
  if (usedNonces.has(nonce)) {
    res.status(409).json({
      success: false,
      message: 'Duplicate request detected'
    });
    return;
  }

  // Check timestamp is not too old
  const currentTime = Date.now();
  if (currentTime - requestTime > NONCE_EXPIRY_MS) {
    res.status(400).json({
      success: false,
      message: 'Request has expired'
    });
    return;
  }

  // Mark nonce as used
  usedNonces.add(nonce);

  // Periodically clean up expired nonces
  setTimeout(() => {
    usedNonces.delete(nonce);
  }, NONCE_EXPIRY_MS);

  next();
};

// Helper function for clients to generate nonces
export const generateNonce = (): { nonce: string, timestamp: number } => {
  return {
    nonce: uuidv4(),
    timestamp: Date.now()
  };
};