import { transactionIdValidation } from '../../src/middleware/transaction-id-validation';
import { v4 as uuidv4 } from 'uuid';
import { Request, Response, NextFunction } from 'express';

describe('Transaction ID Validation Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;

  beforeEach(() => {
    mockRequest = {};
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    nextFunction = jest.fn();
  });

  test('should generate a new UUID if no transaction ID is provided', () => {
    transactionIdValidation(
      mockRequest as Request, 
      mockResponse as Response, 
      nextFunction
    );

    expect(mockRequest.transactionId).toBeDefined();
    expect(mockRequest.transactionId).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    expect(nextFunction).toHaveBeenCalled();
  });

  test('should accept a valid transaction ID from headers', () => {
    const validUuid = uuidv4();
    mockRequest.headers = { 'x-transaction-id': validUuid };

    transactionIdValidation(
      mockRequest as Request, 
      mockResponse as Response, 
      nextFunction
    );

    expect(mockRequest.transactionId).toBe(validUuid);
    expect(nextFunction).toHaveBeenCalled();
  });

  test('should accept a valid transaction ID from body', () => {
    const validUuid = uuidv4();
    mockRequest.body = { transactionId: validUuid };

    transactionIdValidation(
      mockRequest as Request, 
      mockResponse as Response, 
      nextFunction
    );

    expect(mockRequest.transactionId).toBe(validUuid);
    expect(nextFunction).toHaveBeenCalled();
  });

  test('should accept a valid transaction ID from query', () => {
    const validUuid = uuidv4();
    mockRequest.query = { transactionId: validUuid };

    transactionIdValidation(
      mockRequest as Request, 
      mockResponse as Response, 
      nextFunction
    );

    expect(mockRequest.transactionId).toBe(validUuid);
    expect(nextFunction).toHaveBeenCalled();
  });

  test('should reject an invalid transaction ID', () => {
    mockRequest.headers = { 'x-transaction-id': 'invalid-uuid' };

    transactionIdValidation(
      mockRequest as Request, 
      mockResponse as Response, 
      nextFunction
    );

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        error: 'Invalid transaction ID format',
        message: 'Transaction ID must be a valid UUID'
      })
    );
    expect(nextFunction).not.toHaveBeenCalled();
  });
});