import { verifySignature, signData } from '../../src/utils/sign';
import nacl from 'tweetnacl';
import { Keypair } from '@_koii/web3.js';
import bs58 from 'bs58';

describe('Signature Utility', () => {
  let keypair: Keypair;
  let stakingKey: string;

  beforeAll(() => {
    // Generate a new keypair for testing
    const keyPairBytes = nacl.sign.keyPair();
    keypair = {
      publicKey: keyPairBytes.publicKey,
      secretKey: keyPairBytes.secretKey
    };
    stakingKey = bs58.encode(keypair.publicKey);
  });

  it('should successfully sign and verify data', async () => {
    const testData = { message: 'Test message' };
    const signature = await signData(keypair, testData);
    
    const verificationResult = await verifySignature(signature, stakingKey);
    
    expect(verificationResult.error).toBeUndefined();
    expect(verificationResult.data).toBeDefined();
    
    const parsedData = JSON.parse(verificationResult.data || '{}');
    expect(parsedData).toEqual(testData);
  });

  it('should fail verification with invalid signature', async () => {
    const invalidSignature = 'invalidSignatureString';
    const verificationResult = await verifySignature(invalidSignature, stakingKey);
    
    expect(verificationResult.error).toBeDefined();
    expect(verificationResult.data).toBeUndefined();
  });

  it('should fail verification with incorrect staking key', async () => {
    const testData = { message: 'Test message' };
    const signature = await signData(keypair, testData);
    
    const incorrectStakingKey = bs58.encode(nacl.randomBytes(32));
    const verificationResult = await verifySignature(signature, incorrectStakingKey);
    
    expect(verificationResult.error).toBeDefined();
    expect(verificationResult.data).toBeUndefined();
  });
});