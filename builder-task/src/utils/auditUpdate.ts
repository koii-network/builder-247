import { namespaceWrapper } from "@_koii/namespace-wrapper";

/**
 * Function to trigger the update-audit-result endpoint to update todo and issue statuses
 * This will update todos that were approved in audits and make issues ready for leader round
 */
export async function triggerAuditUpdate(
  taskId: string,
  round: number,
  stakingKeypair: any,
  orcaClient: any,
): Promise<void> {
  try {
    console.log(`Triggering audit update for worker round ${round}`);
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();

    // Create the payload for the update-audit-result endpoint
    const updatePayload = {
      taskId,
      round,
      action: "update-audit-result",
      stakingKey,
      pubKey,
      githubUsername: process.env.GITHUB_USERNAME,
    };

    // Sign the payload
    const signature = await namespaceWrapper.payloadSigning(updatePayload, stakingKeypair.secretKey);

    // Make the request
    const response = await orcaClient.podCall(`update-audit-result/${taskId}/${round}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        taskId,
        round,
        signature,
        stakingKey,
        pubKey,
      }),
    });

    console.log("Audit update response:", response);
  } catch (error) {
    console.error("Error triggering audit update:", error);
  }
}
