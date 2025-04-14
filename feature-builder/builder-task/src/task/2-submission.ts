import { storeFile } from "../utils/ipfs";
import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";

export async function submission(roundNumber: number) {
  /**
   * Retrieve the task proofs from your container and submit for auditing
   * Must return a string of max 512 bytes to be submitted on chain
   * The default implementation handles uploading the proofs to IPFS
   * and returning the CID
   */
  console.log(`FETCH SUBMISSION FOR ROUND ${roundNumber}`);
  try {
    const orcaClient = await getOrcaClient();
    const result = await orcaClient.podCall(`submission/${TASK_ID}/${roundNumber}`);
    let submission;

    console.log({ "submission result": result.data });

    if (result.data === "No submission") {
      return "submission";
    } else {
      submission = result.data;
    }

    if (submission.roundNumber !== roundNumber) {
      throw new Error("Submission is not for the current round");
    }

    if (!submission.prUrl) {
      throw new Error("Submission is missing PR URL");
    }

    console.log({ submission });

    // if you are writing a KPL task, use namespaceWrapper.getSubmitterAccount("KPL");
    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();

    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }

    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();

    // sign the submission
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

    // store the submission on IPFS
    const cid = await storeFile({ signature }, "submission.json");
    console.log("SUBMISSION CID:", cid);
    return cid;
  } catch (error) {
    console.error("FETCH SUBMISSION ERROR:", error);
  }
}
