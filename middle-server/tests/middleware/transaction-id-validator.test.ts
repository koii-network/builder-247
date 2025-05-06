import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { transactionIdValidator } from '../../src/middleware/transaction-id-validator';
import { Logger } from '../../src/utils/logging'; // Mocked logger

// Mock the logger to prevent actual logging during tests
jest.mock('../../src/utils/logging', () => ({
  Logger: {
    warn: jest.fn(),
    info: jest.fn()
  }
}));

describe('Transaction ID Validator Middleware', () => {
  let mockReq: Partial<Request>;
  let mockRes: Partial<Response>;
  let mockNext: jest.MockedFunction<NextFunction>;

  beforeEach(() => {
    mockReq = {
      headers: {},
      ip: '127.0.0.1'
    };
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
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

  it('should reject duplicate transaction IDs', () => {
    const duplicateTransactionId = uuidv4();
    mockReq.headers = { 'x-transaction-id': duplicateTransactionId };

    // First request should pass
    transactionIdValidator(mockReq as Request, mockRes as Response, mockNext);
    expect(mockNext).toHaveBeenCalled();

    // Reset mocks for second request
    mockNext.mockClear();
    (mockRes.status as jest.Mock).mockClear();
    (mockRes.json as jest.Mock).mockClear();

    // Second request with same transaction ID should be rejected
    transactionIdValidator(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(409);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Duplicate Transaction ID'
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

  it('should log validation events', () => {
    const validTransactionId = uuidv4();
    mockReq.headers = { 'x-transaction-id': validTransactionId };

    transactionIdValidator(mockReq as Request, mockRes as Response, mockNext);

    expect(Logger.info).toHaveBeenCalledWith(
      'Transaction ID Validated', 
      expect.objectContaining({
        transactionId: validTransactionId
      })
    );
  });
});