import { getOrcaClient } from "@_koii/task-manager/extensions";
import { middleServerUrl, status } from "../utils/constant";
import { submissionJSONSignatureDecode } from "../utils/submissionJSONSignatureDecode";
// import { status } from '../utils/constant'
export async function audit(cid: string, roundNumber: number, submitterKey: string): Promise<boolean | void> {
  /**
   * Audit a submission
   * This function should return true if the submission is correct, false otherwise
   * The default implementation retrieves the proofs from IPFS
   * and sends them to your container for auditing
   */

  try {
    const orcaClient = await getOrcaClient();
    if (!orcaClient) {
      // await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_ORCA_CLIENT);
      return;
    }
    // Check if the cid is one of the status
    if (Object.values(status).includes(cid)) {
      // This returns a dummy true
      return true;
    }
    const decodeResult = await submissionJSONSignatureDecode({
      submission_value: cid,
      submitterPublicKey: submitterKey,
      roundNumber: roundNumber,
    });
    if (!decodeResult) {
      console.log("[AUDIT] DECODE RESULT FAILED.");
      return false;
    }
    console.log(`[AUDIT] ✅ Signature decoded successfully`);

    console.log(`[AUDIT] Checking summarizer status for submitter ${submitterKey}`);
    const checkSummarizerResponse = await fetch(`${middleServerUrl}/summarizer/worker/check-todo`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        stakingKey: submitterKey,
        roundNumber,
        githubUsername: decodeResult.githubUsername,
        prUrl: decodeResult.prUrl,
      }),
    });
    const checkSummarizerJSON = await checkSummarizerResponse.json();
    console.log(`[AUDIT] Summarizer check response:`, checkSummarizerJSON);

    if (!checkSummarizerJSON.success) {
      console.log(`[AUDIT] ❌ Audit failed for ${submitterKey}`);
      return false;
    }
    console.log(`[AUDIT] ✅ Summarizer check passed`);

    console.log(`[AUDIT] Sending audit request for submitter: ${submitterKey}`);
    console.log(`[AUDIT] Submission data being sent to audit:`, decodeResult);

    const result = await orcaClient.podCall(`worker-audit/${roundNumber}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        submission: decodeResult,
      }),
    });

    console.log(`[AUDIT] Raw audit result:`, result);
    console.log(`[AUDIT] Audit result data type:`, typeof result.data);
    console.log(`[AUDIT] Audit result data value:`, result.data);

    if (result.data === true) {
      console.log(`[AUDIT] ✅ Audit passed for ${submitterKey}`);
      return true;
    } else {
      console.log(`[AUDIT] ❌ Audit failed for ${submitterKey}`);
      console.log(`[AUDIT] Failed audit result data:`, result.data);
      return false;
    }
  } catch (error) {
    console.error("[AUDIT] Error auditing submission:", error);

    // When Error---NO RETURN;
    // return true;
  }
}
