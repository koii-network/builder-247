import { signData, verifySignature } from "../../src/utils/sign";
import { Keypair } from "@_koii/web3.js";

const keypair = Keypair.generate();
async function main() {
  const body = {
    roundNumber: 1,
    taskId: "tempSimulateTaskID",
    pubKey: "tempSimulatePubKey",
  };

  const signedMessage = await signData(keypair, body);

  const verified = await verifySignature(
    signedMessage,
    keypair.publicKey.toBase58(),
  );

  console.log(verified);
}
main();
