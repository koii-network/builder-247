import { validateTransactionId } from '../../src/middleware/transaction-id-validation';
import { v4 as uuidv4 } from 'uuid';

describe('Transaction ID Validation Middleware', () => {
  let mockReq: any;
  let mockRes: any;
  let mockNext: jest.Mock;

  beforeEach(() => {
    mockReq = {
      headers: {},
      body: {},
      query: {}
    };
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  it('should generate a new transaction ID if none is provided', () => {
    validateTransactionId(mockReq, mockRes, mockNext);

    expect(mockReq.transactionId).toBeDefined();
    expect(uuidv4.validate(mockReq.transactionId)).toBeTruthy();
    expect(mockNext).toHaveBeenCalled();
  });

  it('should accept a valid transaction ID from headers', () => {
    const validUuid = uuidv4();
    mockReq.headers['x-transaction-id'] = validUuid;

    validateTransactionId(mockReq, mockRes, mockNext);

    expect(mockReq.transactionId).toBe(validUuid);
    expect(mockNext).toHaveBeenCalled();
  });

  it('should accept a valid transaction ID from body', () => {
    const validUuid = uuidv4();
    mockReq.body.transactionId = validUuid;

    validateTransactionId(mockReq, mockRes, mockNext);

    expect(mockReq.transactionId).toBe(validUuid);
    expect(mockNext).toHaveBeenCalled();
  });

  it('should accept a valid transaction ID from query', () => {
    const validUuid = uuidv4();
    mockReq.query.transactionId = validUuid;

    validateTransactionId(mockReq, mockRes, mockNext);

    expect(mockReq.transactionId).toBe(validUuid);
    expect(mockNext).toHaveBeenCalled();
  });

  it('should reject an invalid transaction ID', () => {
    mockReq.headers['x-transaction-id'] = 'invalid-uuid';

    validateTransactionId(mockReq, mockRes, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Invalid Transaction ID',
      message: 'Transaction ID must be a valid UUID v4'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should handle transaction ID priority: headers > body > query', () => {
    const headerUuid = uuidv4();
    const bodyUuid = uuidv4();
    const queryUuid = uuidv4();

    mockReq.headers['x-transaction-id'] = headerUuid;
    mockReq.body.transactionId = bodyUuid;
    mockReq.query.transactionId = queryUuid;

    validateTransactionId(mockReq, mockRes, mockNext);

    expect(mockReq.transactionId).toBe(headerUuid);
    expect(mockNext).toHaveBeenCalled();
  });
});