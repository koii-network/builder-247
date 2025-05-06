import { Request, Response, NextFunction } from 'express';
import { preventReplayAttack, generateNonce } from '../../src/middleware/auth';

describe('Replay Attack Prevention Middleware', () => {
  let mockReq: Partial<Request>;
  let mockRes: Partial<Response>;
  let mockNext: jest.MockedFunction<NextFunction>;

  beforeEach(() => {
    const { nonce, timestamp } = generateNonce();
    mockReq = {
      headers: {
        'x-request-nonce': nonce,
        'x-request-timestamp': timestamp.toString(),
        authorization: 'Bearer test-token'
      }
    };
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  test('should allow valid request', () => {
    process.env.PROMETHEUS_INCOME_REQUEST_API_KEY = 'test-token';
    preventReplayAttack(mockReq as Request, mockRes as Response, mockNext);
    expect(mockNext).toHaveBeenCalled();
  });

  test('should reject request without nonce', () => {
    delete mockReq.headers['x-request-nonce'];
    preventReplayAttack(mockReq as Request, mockRes as Response, mockNext);
    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Request nonce is required'
    }));
  });

  test('should reject request with invalid timestamp', () => {
    mockReq.headers['x-request-timestamp'] = 'invalid';
    preventReplayAttack(mockReq as Request, mockRes as Response, mockNext);
    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Invalid request timestamp'
    }));
  });

  test('should reject duplicate nonce', () => {
    // First request
    preventReplayAttack(mockReq as Request, mockRes as Response, mockNext);
    expect(mockNext).toHaveBeenCalled();

    // Duplicate request
    preventReplayAttack(mockReq as Request, mockRes as Response, mockNext);
    expect(mockRes.status).toHaveBeenCalledWith(409);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Duplicate request detected'
    }));
  });

  test('should reject expired request', () => {
    const pastTimestamp = Date.now() - (6 * 60 * 1000); // 6 minutes ago
    mockReq.headers['x-request-timestamp'] = pastTimestamp.toString();
    preventReplayAttack(mockReq as Request, mockRes as Response, mockNext);
    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Request has expired'
    }));
  });
});

describe('Nonce Generation', () => {
  test('should generate unique nonces', () => {
    const nonce1 = generateNonce();
    const nonce2 = generateNonce();

    expect(nonce1.nonce).not.toEqual(nonce2.nonce);
    expect(nonce1.timestamp).not.toEqual(nonce2.timestamp);
  });
});