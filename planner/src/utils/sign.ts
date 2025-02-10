import nacl from "tweetnacl";
import { Keypair } from "@_koii/web3.js";
import bs58 from "bs58";

async function bs58Decode(data: string): Promise<Uint8Array> {
	return new Uint8Array(bs58.decode(data));
}

function decodePayload(payload: Uint8Array): string {
	return new TextDecoder().decode(payload);
}

export async function verifySignature(
	signedMessage: string,
	pubKey: string
): Promise<{ data?: string; error?: string }> {
	console.log("signedMessage", signedMessage);
	console.log("pubKey", pubKey);
	try {
		const payload = nacl.sign.open(
			await bs58Decode(signedMessage),
			await bs58Decode(pubKey)
		);
		if (!payload) return { error: "Invalid signature" };
		return { data: decodePayload(payload) };
	} catch (e) {
		console.error(e);
		return { error: `Verification failed: ${e}` };
	}
}
