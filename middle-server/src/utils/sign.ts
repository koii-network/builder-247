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

async function bs58Decode(data: string): Promise<Uint8Array> {
  return new Uint8Array(bs58.decode(data));
}

function decodePayload(payload: Uint8Array): string {
  return new TextDecoder().decode(payload);
}

export async function verifySignature(
  signedMessage: string,
  stakingKey: string,
): Promise<{ data?: string; error?: string }> {
  try {
    const payload = nacl.sign.open(await bs58Decode(signedMessage), await bs58Decode(stakingKey));
    if (!payload) return { error: "Invalid signature" };
    return { data: decodePayload(payload) };
  } catch (e) {
    console.error(e);
    return { error: `Verification failed: ${e}` };
  }
}
