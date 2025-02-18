import { storeFile } from "../helpers.js";
import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";


export async function submission(roundNumber: number): Promise<string | void>  {
  /**
   * Retrieve the task proofs from your container and submit for auditing
   * Must return a string of max 512 bytes to be submitted on chain
   * The default implementation handles uploading the proofs to IPFS
   * and returning the CID
   */
  console.log(`FETCH SUBMISSION FOR ROUND ${roundNumber}`);
  try {
    const orcaClient = await getOrcaClient();
    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
        if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    console.log("stakingKey", stakingKey);
    const result = await orcaClient.podCall(`submission/${roundNumber}`);
    result.data.stakingKey = stakingKey;
    const signature = await namespaceWrapper.payloadSigning(
      {
        taskId: TASK_ID,
        roundNumber: roundNumber,
        action: "check",
      },
      stakingKeypair.secretKey,
    );
    result.data.signature = signature;
    const cid = await storeFile(result.data, "submission.json");
    console.log("SUBMISSION CID:", cid);
    return cid;
  } catch (error) {
    console.error("FETCH SUBMISSION ERROR:", error);
  }
}
