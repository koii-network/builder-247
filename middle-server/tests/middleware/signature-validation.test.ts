import { signatureValidationMiddleware } from '../../src/middleware/signature-validation';
import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';

describe('Signature Validation Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: jest.MockedFunction<NextFunction>;

  // Generate a key pair for testing
  const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
  });

  beforeEach(() => {
    // Reset mocks before each test
    mockRequest = {
      body: { test: 'data' },
      headers: {}
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  it('should call next() when signature is valid', () => {
    // Create a valid signature
    const bodyString = JSON.stringify(mockRequest.body);
    const signer = crypto.createSign('SHA256');
    signer.update(bodyString);
    const signature = signer.sign(privateKey).toString('base64');

    // Set headers
    mockRequest.headers = {
      'x-signature': signature,
      'x-public-key': publicKey.export({ type: 'spki', format: 'pem' })
    };

    // Call middleware
    signatureValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    // Expect next to be called
    expect(mockNext).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
  });

  it('should return 400 when signature is missing', () => {
    // Call middleware without signature
    signatureValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    // Expect error response
    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({ error: 'Missing signature or public key' })
    );
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should return 403 when signature is invalid', () => {
    // Set headers with invalid signature
    mockRequest.headers = {
      'x-signature': 'invalid-signature',
      'x-public-key': publicKey.export({ type: 'spki', format: 'pem' })
    };

    // Call middleware
    signatureValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    // Expect error response
    expect(mockResponse.status).toHaveBeenCalledWith(403);
    expect(mockResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({ error: 'Invalid signature' })
    );
    expect(mockNext).not.toHaveBeenCalled();
  });
});