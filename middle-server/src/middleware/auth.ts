import { Request, Response, NextFunction } from 'express';

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

  // In a real application, you would verify the token against your authentication system
  // For now, we'll just check if it matches the expected token from environment variables
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