import { validateTransactionId } from '../../src/middleware/transaction_id_validation';
import { v4 as uuidv4 } from 'uuid';

describe('Transaction ID Validation Middleware', () => {
  let mockRequest: any;
  let mockResponse: any;
  let mockNext: jest.Mock;

  beforeEach(() => {
    mockRequest = {
      headers: {},
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
    };
    mockNext = jest.fn();
  });

  it('should reject request with no transaction ID', () => {
    validateTransactionId(mockRequest, mockResponse, mockNext);

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Transaction ID is required'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should reject request with empty transaction ID', () => {
    mockRequest.headers['x-transaction-id'] = '';

    validateTransactionId(mockRequest, mockResponse, mockNext);

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Invalid Transaction ID',
      message: 'Transaction ID cannot be an empty string'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should reject request with whitespace-only transaction ID', () => {
    mockRequest.headers['x-transaction-id'] = '   ';

    validateTransactionId(mockRequest, mockResponse, mockNext);

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Invalid Transaction ID',
      message: 'Transaction ID cannot be an empty string'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should reject request with invalid UUID', () => {
    mockRequest.headers['x-transaction-id'] = 'not-a-uuid';

    validateTransactionId(mockRequest, mockResponse, mockNext);

    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Invalid Transaction ID',
      message: 'Transaction ID must be a valid UUID v4'
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should accept valid UUID v4 transaction ID', () => {
    const validUuid = uuidv4();
    mockRequest.headers['x-transaction-id'] = validUuid;

    validateTransactionId(mockRequest, mockResponse, mockNext);

    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockNext).toHaveBeenCalled();
    expect(mockRequest.validatedTransactionId).toBe(validUuid);
  });

  it('should trim whitespace around valid UUID', () => {
    const validUuid = uuidv4();
    mockRequest.headers['x-transaction-id'] = `  ${validUuid}  `;

    validateTransactionId(mockRequest, mockResponse, mockNext);

    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockNext).toHaveBeenCalled();
    expect(mockRequest.validatedTransactionId).toBe(validUuid);
  });
});