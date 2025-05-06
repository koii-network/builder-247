import { Request, Response, NextFunction } from 'express';
import { validateSignature } from '../../src/middleware/signature_validation';
import { signData, verifySignature } from '../../src/utils/sign';
import { Keypair } from '@_koii/web3.js';

describe('Signature Validation Middleware', () => {
  let mockReq: any;
  let mockRes: any;
  let mockNext: jest.MockedFunction<NextFunction>;

  beforeEach(() => {
    mockNext = jest.fn();
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
  });

  it('should return 400 if signature or staking key is missing', async () => {
    mockReq = {
      headers: {},
      body: {}
    };

    await validateSignature(mockReq, mockRes, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Missing signature or staking key'
    }));
  });

  it('should validate a correct signature', async () => {
    // Generate keypair for testing
    const keypair = Keypair.generate();
    const body = { test: 'data' };

    // Sign the data
    const signature = await signData(keypair, body);

    mockReq = {
      headers: {
        'x-signature': signature,
        'x-staking-key': bs58.encode(keypair.publicKey.toBytes())
      },
      body
    };

    await validateSignature(mockReq, mockRes, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect(mockReq.verifiedData).toEqual(body);
  });

  it('should return 401 for an invalid signature', async () => {
    const keypair = Keypair.generate();
    const body = { test: 'data' };

    // Sign with one keypair
    const signature = await signData(keypair, body);

    // Use a different keypair for verification to cause failure
    const wrongKeypair = Keypair.generate();

    mockReq = {
      headers: {
        'x-signature': signature,
        'x-staking-key': bs58.encode(wrongKeypair.publicKey.toBytes())
      },
      body
    };

    await validateSignature(mockReq, mockRes, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(401);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'Signature verification failed'
    }));
  });
});