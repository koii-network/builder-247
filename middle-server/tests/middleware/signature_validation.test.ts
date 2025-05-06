import { signatureValidationMiddleware } from '../../src/middleware/signature_validation';
import { Request, Response, NextFunction } from 'express';

// Mock the sign utility
jest.mock('../../src/utils/sign', () => ({
  verifySignature: jest.fn()
}));

import { verifySignature } from '../../src/utils/sign';

describe('Signature Validation Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: jest.MockedFunction<NextFunction>;

  beforeEach(() => {
    mockRequest = {
      body: {
        data: { key: 'value' },
        signature: 'valid_signature'
      }
    };

    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    mockNext = jest.fn();

    // Reset the mock before each test
    (verifySignature as jest.Mock).mockReset();
  });

  test('should call next() when signature is valid', () => {
    (verifySignature as jest.Mock).mockReturnValue(true);

    signatureValidationMiddleware(
      mockRequest as Request,
      mockResponse as Response,
      mockNext
    );

    expect(verifySignature).toHaveBeenCalledWith(
      mockRequest.body.data,
      mockRequest.body.signature
    );
    expect(mockNext).toHaveBeenCalled();
  });

  test('should return 403 when signature is invalid', () => {
    (verifySignature as jest.Mock).mockReturnValue(false);

    signatureValidationMiddleware(
      mockRequest as Request,
      mockResponse as Response,
      mockNext
    );

    expect(verifySignature).toHaveBeenCalledWith(
      mockRequest.body.data,
      mockRequest.body.signature
    );
    expect(mockResponse.status).toHaveBeenCalledWith(403);
    expect(mockResponse.json).toHaveBeenCalledWith({
      error: 'Invalid signature: Request authenticity could not be verified',
      success: false
    });
    expect(mockNext).not.toHaveBeenCalled();
  });

  test('should return 400 when signature or data is missing', () => {
    mockRequest.body = {};

    signatureValidationMiddleware(
      mockRequest as Request,
      mockResponse as Response,
      mockNext
    );

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith({
      error: 'Signature and data are required for validation',
      success: false
    });
    expect(mockNext).not.toHaveBeenCalled();
  });

  test('should handle server errors', () => {
    (verifySignature as jest.Mock).mockImplementation(() => {
      throw new Error('Test error');
    });

    signatureValidationMiddleware(
      mockRequest as Request,
      mockResponse as Response,
      mockNext
    );

    expect(mockResponse.status).toHaveBeenCalledWith(500);
    expect(mockResponse.json).toHaveBeenCalledWith({
      error: 'Internal server error during signature validation',
      success: false
    });
    expect(mockNext).not.toHaveBeenCalled();
  });
});