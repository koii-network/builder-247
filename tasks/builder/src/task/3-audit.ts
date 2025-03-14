import { getFile } from "../utils/ipfs";
import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import { getLeaderNode } from "../utils/leader";

export async function audit(cid: string, roundNumber: number, submitterKey: string): Promise<boolean | void> {
  /**
   * Audit a submission
   * This function should return true if the submission is correct, false otherwise
   * The default implementation retrieves the proofs from IPFS
   * and sends them to your container for auditing
   */
  try {
    console.log(`AUDIT SUBMISSION FOR ROUND ${roundNumber}`);
    // get the submission from IPFS
    if (cid === "submission") {
      return true;
    }
    const submissionString = await getFile(cid);
    const submission = JSON.parse(submissionString);
    console.log({ submission });

    // verify the signature of the submission
    const signaturePayload = await namespaceWrapper.verifySignature(submission.signature, submitterKey);

    // verify the signature payload
    if (signaturePayload.error || !signaturePayload.data) {
      console.error("INVALID SIGNATURE");
      return false;
    }
    const data = JSON.parse(signaturePayload.data);

    if (
      data.taskId !== TASK_ID ||
      data.roundNumber !== roundNumber ||
      data.stakingKey !== submitterKey ||
      !data.pubKey ||
      !data.prUrl
    ) {
      console.error("INVALID SIGNATURE DATA");
      return false;
    }

    const orca = await getOrcaClient();

    const { isLeader } = await getLeaderNode({ roundNumber, leaderNumber: 1, submitterPublicKey: submitterKey });
    let podCallUrl;

    if (isLeader) {
      podCallUrl = `leader-audit/${roundNumber}`;
    } else {
      podCallUrl = `worker-audit/${roundNumber}`;
    }
    const auditResult = await orca.podCall(podCallUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        submission: data,
        signature: submission.signature,
        stakingKey: submitterKey,
        pubKey: data.pubKey,
      }),
    });

    // return the result of the audit (true or false)
    return auditResult.data;
  } catch (error) {
    console.error("ERROR AUDITING SUBMISSION", error);
    return true;
  }
}
