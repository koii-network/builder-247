import { storeFile } from "../utils/ipfs";
import { getOrcaClient } from "@_koii/task-manager/extensions";
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
    const orcaClient = await getOrcaClient();
    if (!orcaClient) {
      console.error("[SUBMISSION] Failed to initialize Orca client");
      return;
    }
    console.log("[SUBMISSION] Orca client initialized successfully");

    console.log(`[SUBMISSION] Fetching task result for round ${roundNumber}...`);
    const taskResult = await namespaceWrapper.storeGet(`result-${roundNumber}`);
    if (!taskResult) {
      console.log("[SUBMISSION] No task result found for this round");
      return status.NO_DATA_FOR_THIS_ROUND;
    }
    console.log(`[SUBMISSION] Task result status: ${taskResult}`);

    if (taskResult !== status.ISSUE_SUCCESSFULLY_SUMMARIZED) {
      console.log(`[SUBMISSION] Task not successfully summarized. Status: ${taskResult}`);
      return taskResult;
    }

    console.log(`[SUBMISSION] Fetching submission data for round ${roundNumber}...`);

    let ipfsCid = await namespaceWrapper.storeGet(`ipfs-cid-${roundNumber}`);
    if (!ipfsCid) {
      console.error("[SUBMISSION] No IPFS CID found for this round");
      return status.NO_IPFS_CID_FOUND_FOR_THIS_ROUND;
    }
    let submission = {
      prUrl: ipfsCid,
    };
    console.log("[SUBMISSION] Submission data validated successfully:", submission);

    console.log("[SUBMISSION] Getting submitter account...");
    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();

    if (!stakingKeypair) {
      console.error("[SUBMISSION] No staking keypair found");
      throw new Error("No staking keypair found");
    }
    console.log("[SUBMISSION] Submitter account retrieved successfully");

    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    console.log("[SUBMISSION] Staking key:", stakingKey);
    console.log("[SUBMISSION] Public key:", pubKey);

    console.log("[SUBMISSION] Signing submission payload...");
    const signature = await namespaceWrapper.payloadSigning(
      {
        taskId: TASK_ID,
        roundNumber,
        stakingKey,
        pubKey,
        action: "audit",
        ...submission,
      },
      stakingKeypair.secretKey,
    );
    console.log("[SUBMISSION] Payload signed successfully");

    console.log("[SUBMISSION] Storing submission on IPFS...");
    const cid = await storeFile({ signature }, "submission.json");
    console.log("[SUBMISSION] Submission stored successfully. CID:", cid);
    return cid || void 0;
  } catch (error) {
    console.error("[SUBMISSION] Error during submission process:", error);
    throw error;
  }
}
