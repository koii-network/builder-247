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

    if (data.prUrl === "none") {
      console.log("Dummy submission");
      return true;
    }

    const orca = await getOrcaClient();

    const { isLeader } = await getLeaderNode({ roundNumber, leaderNumber: 1, submitterPublicKey: submitterKey });
    let podCallUrl;

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
      distributionList?: Record<string, number>;
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

    if (isLeader) {
      podCallUrl = `leader-audit/${roundNumber}`;

      // For leader audits, we need to get the distribution list
      try {
        console.log("Fetching distribution list for leader audit of round", roundNumber);
        const distributionList = await namespaceWrapper.getDistributionList(submitterKey, roundNumber);

        if (!distributionList) {
          console.log("No distribution list available for this round, failing leader audit");
          return false;
        }

        try {
          const parsedDistributionList = JSON.parse(distributionList);

          if (Object.keys(parsedDistributionList).length === 0) {
            console.log("Distribution list is empty, failing leader audit");
            return false;
          }

          // Get submissions for this round to filter out ineligible ones
          const submissionsResponse = await orca.podCall(`submission/${roundNumber}`);
          const submissions = submissionsResponse.data;

          if (!Array.isArray(submissions)) {
            console.log("No valid submissions data available, failing leader audit");
            return false;
          }

          // Create filtered distribution list excluding ineligible nodes
          const filteredDistributionList: Record<string, number> = {};
          for (const [stakingKey, amount] of Object.entries(parsedDistributionList)) {
            const numericAmount = amount as number;

            // Skip if amount is zero or negative (failed audit)
            if (numericAmount <= 0) {
              console.log(`Audit: Skipping staking key ${stakingKey} due to zero/negative reward: ${numericAmount}`);
              continue;
            }

            // Find corresponding submission
            const submission = submissions.find((s) => s.stakingKey === stakingKey);

            // Skip if no submission found
            if (!submission) {
              console.log(`Audit: Skipping staking key ${stakingKey} - no submission found`);
              continue;
            }

            // Skip if submission has no PR URL or is a dummy submission
            if (!submission.prUrl || submission.prUrl === "none") {
              console.log(`Audit: Skipping staking key ${stakingKey} - no valid PR URL`);
              continue;
            }

            // Node is eligible, include in filtered list
            filteredDistributionList[stakingKey] = numericAmount;
            console.log(`Audit: Including eligible node ${stakingKey} with amount ${numericAmount}`);
          }

          if (Object.keys(filteredDistributionList).length === 0) {
            console.log("No eligible nodes in distribution list after filtering, failing leader audit");
            return false;
          }

          // Add filtered distribution list to podCallBody for leader audit
          podCallBody.distributionList = filteredDistributionList;
          console.log(
            "Audit: Successfully filtered distribution list. Eligible nodes:",
            Object.keys(filteredDistributionList).length,
          );
        } catch (parseError) {
          console.error("Failed to parse distribution list during audit:", parseError);
          console.log("Raw distribution list:", distributionList);
          return false;
        }
      } catch (distError) {
        console.error("Error fetching distribution list during audit:", distError);
        return false;
      }
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

    // return the result of the audit (true or false)
    return auditResult.data;
  } catch (error) {
    console.error("ERROR AUDITING SUBMISSION", error);
    return true;
  }
}
