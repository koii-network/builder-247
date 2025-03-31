import { Keypair } from "@_koii/web3.js";
import { signData, verifySignature } from "../../src/utils/sign";
import bs58 from "bs58";

describe("Sign Utils", () => {
  let keypair: Keypair;

  beforeAll(() => {
    keypair = Keypair.generate();
  });

  describe("signData", () => {
    it("should successfully sign data", async () => {
      const testData = { test: "Hello World" };
      const signature = await signData(keypair, testData);
      expect(typeof signature).toBe("string");
      expect(() => bs58.decode(signature)).not.toThrow();
    });
  });

  describe("verifySignature", () => {
    it("should verify valid signature successfully", async () => {
      const testData = { message: "Test Message" };
      const signature = await signData(keypair, testData);
      const publicKey = bs58.encode(Buffer.from(keypair.publicKey.toBytes()));

      const result = await verifySignature(signature, publicKey);

      expect(result.error).toBeUndefined();
      expect(result.data).toBeDefined();
      expect(JSON.parse(result.data!)).toEqual(testData);
    });

    it("should reject invalid signature", async () => {
      const invalidSignature = bs58.encode(Buffer.from("invalid signature"));
      const publicKey = bs58.encode(Buffer.from(keypair.publicKey.toBytes()));

      const result = await verifySignature(invalidSignature, publicKey);

      expect(result.error).toBeDefined();
      expect(result.data).toBeUndefined();
    });

    it("should reject when using wrong public key", async () => {
      const testData = { message: "Test Message" };
      const signature = await signData(keypair, testData);
      const wrongKeypair = Keypair.generate();
      const wrongPublicKey = bs58.encode(
        Buffer.from(wrongKeypair.publicKey.toBytes()),
      );

      const result = await verifySignature(signature, wrongPublicKey);

      expect(result.error).toBeDefined();
      expect(result.data).toBeUndefined();
    });
  });
});
