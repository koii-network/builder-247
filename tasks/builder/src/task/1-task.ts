import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getLeaderNode } from "../utils/leader";

interface PodCallBody {
  taskId?: string;
  roundNumber: number;
  stakingKey: string;
  pubKey: string;
  stakingSignature: string;
  publicSignature: string;
  distributionList?: Record<string, number>;
}
export async function task(roundNumber: number): Promise<void> {
  /**
   * Run your task and store the proofs to be submitted for auditing
   * It is expected you will store the proofs in your container
   * The submission of the proofs is done in the submission function
   */
  console.log(`EXECUTE TASK FOR ROUND ${roundNumber}`);
  try {
    const orcaClient = await getOrcaClient();

    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    if (!pubKey) {
      throw new Error("No public key found");
    }
    const { isLeader, leaderNode } = await getLeaderNode({ roundNumber, submitterPublicKey: stakingKey });
    const payload = {
      taskId: TASK_ID,
      roundNumber,
      githubUsername: process.env.GITHUB_USERNAME,
      repoOwner: leaderNode,
      stakingKey,
      pubKey,
      action: "task",
    };
    const stakingSignature = await namespaceWrapper.payloadSigning(payload, stakingKeypair.secretKey);
    const publicSignature = await namespaceWrapper.payloadSigning(payload);
    if (!stakingSignature || !publicSignature) {
      throw new Error("Signature generation failed");
    }

    const podCallBody: PodCallBody = {
      taskId: TASK_ID,
      roundNumber,
      stakingKey,
      pubKey,
      stakingSignature,
      publicSignature,
    };
    let podCallUrl;
    if (isLeader) {
      podCallUrl = `leader-task/${roundNumber}`;
      const distributionList = await namespaceWrapper.getDistributionList(TASK_ID!, roundNumber);
      if (distributionList) {
        podCallBody.distributionList = JSON.parse(distributionList);
      }
    } else {
      podCallUrl = `worker-task/${roundNumber}`;
    }
    orcaClient.podCall(podCallUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(podCallBody),
    });
  } catch (error) {
    console.error("EXECUTE TASK ERROR:", error);
  }
}
