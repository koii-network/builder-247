import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { transactionIdValidator } from '../../src/middleware/transaction-id-validator';

describe('Transaction ID Validator Middleware', () => {
  let mockReq: Partial<Request>;
  let mockRes: Partial<Response>;
  let mockNext: jest.MockedFunction<NextFunction>;

  beforeEach(() => {
    mockReq = {
      headers: {}
    };
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  it('should reject requests without transaction ID', () => {
    transactionIdValidator(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Transaction ID is required'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should reject requests with invalid transaction ID', () => {
    mockReq.headers = { 'x-transaction-id': 'invalid-uuid' };

    transactionIdValidator(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Invalid Transaction ID'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should accept requests with valid transaction ID', () => {
    const validTransactionId = uuidv4();
    mockReq.headers = { 'x-transaction-id': validTransactionId };

    transactionIdValidator(mockReq as Request, mockRes as Response, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect((mockReq as any).transactionId).toBe(validTransactionId);
  });
});