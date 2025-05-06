import { verifySignature, signData } from '../../src/utils/sign';
import nacl from 'tweetnacl';
import { Keypair } from "@_koii/web3.js";
import bs58 from 'bs58';

describe('Signature Utilities', () => {
  let keypair: Keypair;
  const testData = { key: 'value', number: 42 };

  beforeAll(() => {
    // Generate a keypair for testing
    const keyPair = nacl.sign.keyPair();
    keypair = {
      publicKey: keyPair.publicKey,
      secretKey: keyPair.secretKey
    } as Keypair;
  });

  describe('verifySignature', () => {
    test('should verify a valid signature', async () => {
      // Sign the data
      const signedData = await signData(keypair, testData);
      
      // Verify the signature
      const isValid = verifySignature(testData, signedData);
      expect(isValid).toBe(true);
    });

    test('should return false for tampered data', async () => {
      const signedData = await signData(keypair, testData);
      const tamperedData = { ...testData, key: 'modified' };

      const isValid = verifySignature(tamperedData, signedData);
      expect(isValid).toBe(false);
    });

    test('should return false for invalid signature', () => {
      const invalidSignature = 'invalid_base58_signature';

      const isValid = verifySignature(testData, invalidSignature);
      expect(isValid).toBe(false);
    });

    test('should handle null/undefined inputs gracefully', () => {
      expect(verifySignature(null as any, 'signature')).toBe(false);
      expect(verifySignature(testData, null as any)).toBe(false);
    });
  });

  describe('signData', () => {
    test('should generate a signature', async () => {
      const signature = await signData(keypair, testData);
      
      // Basic checks
      expect(signature).toBeTruthy();
      expect(typeof signature).toBe('string');
      
      // Verify it's a valid base58 encoded string
      expect(() => bs58.decode(signature)).not.toThrow();
    });
  });
});