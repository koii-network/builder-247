import { storeFile } from "../utils/ipfs";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import { status } from "../utils/constant";
export async function submission(roundNumber: number) : Promise<string | void> {
  /**
   * Retrieve the task proofs from your container and submit for auditing
   * Must return a string of max 512 bytes to be submitted on chain
   * The default implementation handles uploading the proofs to IPFS
   * and returning the CID
   */
  console.log(`[SUBMISSION] Starting submission process for round ${roundNumber}`);

  try {
    console.log("[SUBMISSION] Initializing Orca client...");
    const taskResult = await namespaceWrapper.storeGet(`result-${roundNumber}`);
    if (!taskResult) {
      console.log("[SUBMISSION] No task result found for this round");
      return status.NO_DATA_FOR_THIS_ROUND;
    }
    return taskResult;
  } catch (error) {
    console.error("[SUBMISSION] Error during submission process:", error);
    throw error;
  }
}
