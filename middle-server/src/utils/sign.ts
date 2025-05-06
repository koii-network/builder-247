import nacl from "tweetnacl";
import { Keypair } from "@_koii/web3.js";
// @ts-ignore
import bs58 from "bs58";

export async function signData(keypair: Keypair, body: Record<string, unknown>): Promise<string> {
  const msg = new TextEncoder().encode(JSON.stringify(body));
  const signedMessage = nacl.sign(msg, keypair.secretKey);
  const bs58Encoded = bs58.encode(signedMessage);
  return bs58Encoded;
}

function bs58Decode(data: string): Uint8Array {
  return new Uint8Array(bs58.decode(data));
}

/**
 * Verify the signature of a data payload
 * @param data Original data object
 * @param signature Base58 encoded signed message
 * @returns Boolean indicating whether the signature is valid
 */
export function verifySignature(data: Record<string, unknown>, signature: string): boolean {
  try {
    // Serialize data consistently for verification
    const serializedData = JSON.stringify(data);
    const dataBuffer = new TextEncoder().encode(serializedData);

    // Extract public key from signature (required by NaCl verification)
    const decodedSignature = bs58Decode(signature);
    const signatureBuffer = decodedSignature.slice(64);  // NaCl signature specifics

    // Placeholder public key extraction (modify if needed)
    const publicKey = decodedSignature.slice(0, 64);

    // Verify signature
    return nacl.sign.detached.verify(
      dataBuffer,
      signatureBuffer,
      publicKey
    );
  } catch (error) {
    console.error('Signature verification error:', error);
    return false;
  }
}