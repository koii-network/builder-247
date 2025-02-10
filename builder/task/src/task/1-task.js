import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";

export async function task(roundNumber) {
  /**
   * Run your task and store the proofs to be submitted for auditing
   * It is expected you will store the proofs in your container
   * The submission of the proofs is done in the submission function
   */
  console.log(`EXECUTE TASK FOR ROUND ${roundNumber}`);
  try {
    const orcaClient = await getOrcaClient();

    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    const stakingKey = stakingKeypair.publicKey.toBase58();

    const fetchSignature = await namespaceWrapper.payloadSigning(
      {
        taskId: TASK_ID,
        roundNumber: roundNumber,
        action: "fetch",
      },
      stakingKeypair.secretKey,
    );
    const addSignature = await namespaceWrapper.payloadSigning({
      taskId: TASK_ID,
      roundNumber: roundNumber,
      action: "add",
    });

    await orcaClient.podCall(`task/${roundNumber}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        fetchSignature,
        addSignature,
        stakingKey,
      }),
    });
  } catch (error) {
    console.error("EXECUTE TASK ERROR:", error);
  }
}
