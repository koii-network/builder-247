import { Request, Response, NextFunction } from 'express';
import { v4 as uuid } from 'uuid';
import { transactionIdValidationMiddleware } from '../../src/middleware/transaction-id-validation';

describe('Transaction ID Validation Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: jest.MockedFunction<NextFunction>;

  beforeEach(() => {
    mockRequest = {};
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  it('should pass with a valid transaction ID in headers', () => {
    const validTransactionId = uuid();
    mockRequest.headers = { 'x-transaction-id': validTransactionId };

    transactionIdValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    expect(mockNext).toHaveBeenCalled();
    expect(mockRequest.transactionId).toBe(validTransactionId);
  });

  it('should pass with a valid transaction ID in body', () => {
    const validTransactionId = uuid();
    mockRequest.body = { transactionId: validTransactionId };

    transactionIdValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    expect(mockNext).toHaveBeenCalled();
    expect(mockRequest.transactionId).toBe(validTransactionId);
  });

  it('should return 400 if transaction ID is missing', () => {
    transactionIdValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Transaction ID is required'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should return 400 if transaction ID is not a valid UUID', () => {
    mockRequest.headers = { 'x-transaction-id': 'invalid-uuid' };

    transactionIdValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Invalid Transaction ID'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should handle non-string transaction ID', () => {
    mockRequest.headers = { 'x-transaction-id': 123 as any };

    transactionIdValidationMiddleware(
      mockRequest as Request, 
      mockResponse as Response, 
      mockNext
    );

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Invalid Transaction ID'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });
});