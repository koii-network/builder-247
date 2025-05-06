import { validateSignature, SignedRequest } from '../../src/middleware/signatureValidation';
import { signData } from '../../src/utils/sign';
import { Request, Response, NextFunction } from 'express';
import nacl from 'tweetnacl';
import { Keypair } from '@_koii/web3.js';
import bs58 from 'bs58';

describe('Signature Validation Middleware', () => {
  let mockReq: Partial<SignedRequest>;
  let mockRes: Partial<Response>;
  let mockNext: NextFunction;
  let keypair: Keypair;
  let stakingKey: string;

  beforeEach(() => {
    // Generate a new keypair for each test
    const keyPairBytes = nacl.sign.keyPair();
    keypair = {
      publicKey: keyPairBytes.publicKey,
      secretKey: keyPairBytes.secretKey
    };
    stakingKey = bs58.encode(keypair.publicKey);

    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  it('should validate a correctly signed request', async () => {
    const testData = { message: 'Test request' };
    const signature = await signData(keypair, testData);

    mockReq = {
      headers: {
        'x-signature': signature,
        'x-staking-key': stakingKey
      },
      body: testData
    };

    await validateSignature(
      mockReq as SignedRequest, 
      mockRes as Response, 
      mockNext
    );

    expect(mockNext).toHaveBeenCalled();
    expect(mockReq.validatedData).toEqual(testData);
    expect(mockRes.status).not.toHaveBeenCalled();
  });

  it('should reject request without signature', async () => {
    mockReq = {
      headers: {}
    };

    await validateSignature(
      mockReq as SignedRequest, 
      mockRes as Response, 
      mockNext
    );

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      error: expect.stringContaining('Missing signature')
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should reject request with invalid signature', async () => {
    mockReq = {
      headers: {
        'x-signature': 'invalidSignature',
        'x-staking-key': stakingKey
      }
    };

    await validateSignature(
      mockReq as SignedRequest, 
      mockRes as Response, 
      mockNext
    );

    expect(mockRes.status).toHaveBeenCalledWith(401);
    expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
      error: expect.stringContaining('Invalid signature')
    }));
    expect(mockNext).not.toHaveBeenCalled();
  });
});