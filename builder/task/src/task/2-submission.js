import { storeFile } from "../helpers.js";
import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper } from "@_koii/namespace-wrapper";

export async function submission(roundNumber) {
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
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const result = await orcaClient.podCall(`submission/${roundNumber}`);
    result.stakingKey = stakingKey;
    const cid = await storeFile(result.data, "submission.json");
    console.log("SUBMISSION CID:", cid);
    return cid;
  } catch (error) {
    console.error("FETCH SUBMISSION ERROR:", error);
  }
}
