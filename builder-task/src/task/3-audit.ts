import { getFile } from "../utils/ipfs";
import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
export async function audit(cid: string, roundNumber: number, submitterKey: string): Promise<boolean> {
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

    if (data.prUrl === "none") {
      console.log("Dummy submission");
      return true;
    }

    const isLeader = data.nodeType === "leader";

    const orca = await getOrcaClient();

    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    if (!pubKey) {
      throw new Error("No public key found");
    }
    const payload = {
      taskId: TASK_ID,
      roundNumber: roundNumber,
      prUrl: data.prUrl,
    };
    const stakingSignature = await namespaceWrapper.payloadSigning(payload, stakingKeypair.secretKey);
    const publicSignature = await namespaceWrapper.payloadSigning(payload);
    if (!stakingSignature || !publicSignature) {
      throw new Error("Signature generation failed");
    }

    interface PodCallBody {
      submission: any;
      submitterSignature: any;
      submitterStakingKey: string;
      submitterPubKey: any;
      prUrl: any;
      repoOwner: any;
      repoName: any;
      githubUsername: any;
      stakingKey: string;
      pubKey: string;
      stakingSignature: string;
      publicSignature: string;
    }

    const podCallBody: PodCallBody = {
      submission: data,
      submitterSignature: submission.signature,
      submitterStakingKey: submitterKey,
      submitterPubKey: data.pubKey,
      prUrl: data.prUrl,
      repoOwner: data.repoOwner,
      repoName: data.repoName,
      githubUsername: data.githubUsername,
      stakingKey: stakingKey,
      pubKey: pubKey,
      stakingSignature: stakingSignature,
      publicSignature: publicSignature,
    };

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
      body: JSON.stringify(podCallBody),
    });

    if (auditResult.success) {
      // Log the validation message for debugging
      console.log("Audit result:", auditResult.message);
      // Return the actual boolean result
      return auditResult.data.passed;
    } else {
      console.error("Pod call failed:", auditResult);
      return true; // Keep original behavior of returning true on error
    }
  } catch (error) {
    console.error("ERROR AUDITING SUBMISSION", error);
    return true;
  }
}
