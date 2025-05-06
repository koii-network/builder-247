import { signatureValidationMiddleware } from '../../src/middleware/signature_validation';
import { Request, Response, NextFunction } from 'express';
import { verifySignature } from '../../src/utils/sign';

// Mock the verifySignature function
jest.mock('../../src/utils/sign', () => ({
  verifySignature: jest.fn()
}));

describe('Signature Validation Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;

  beforeEach(() => {
    mockRequest = {
      headers: {},
      body: {}
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  it('should return 400 if signature or public key is missing', async () => {
    await signatureValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith({
      error: 'Missing signature or public key',
      success: false
    });
  });

  it('should return 403 if signature is invalid', async () => {
    (verifySignature as jest.Mock).mockResolvedValue(false);

    mockRequest.headers = {
      'x-signature': 'invalid-signature',
      'x-public-key': 'test-public-key'
    };
    mockRequest.body = { data: 'test' };

    await signatureValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    expect(mockResponse.status).toHaveBeenCalledWith(403);
    expect(mockResponse.json).toHaveBeenCalledWith({
      error: 'Invalid signature',
      success: false
    });
  });

  it('should call next() if signature is valid', async () => {
    (verifySignature as jest.Mock).mockResolvedValue(true);

    mockRequest.headers = {
      'x-signature': 'valid-signature',
      'x-public-key': 'test-public-key'
    };
    mockRequest.body = { data: 'test' };

    await signatureValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    expect(mockNext).toHaveBeenCalled();
  });

  it('should handle server errors gracefully', async () => {
    (verifySignature as jest.Mock).mockRejectedValue(new Error('Test error'));

    mockRequest.headers = {
      'x-signature': 'test-signature',
      'x-public-key': 'test-public-key'
    };
    mockRequest.body = { data: 'test' };

    await signatureValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    expect(mockResponse.status).toHaveBeenCalledWith(500);
    expect(mockResponse.json).toHaveBeenCalledWith({
      error: 'Internal server error during signature validation',
      success: false
    });
  });
});