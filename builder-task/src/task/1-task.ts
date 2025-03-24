import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getLeaderNode } from "../utils/leader";
import { getDistributionList } from "../utils/distributionList";

interface PodCallBody {
  taskId: string;
  roundNumber: number;
  stakingKey: string;
  pubKey: string;
  stakingSignature: string;
  publicSignature: string;
  repoOwner: string;
  repoName: string;
  distributionList: Record<string, any>;
}

interface Submission {
  stakingKey: string;
  prUrl?: string;
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

    const repoData = await orcaClient.podCall(`create-aggregator-repo/${TASK_ID}`, {
      method: "POST",
    });

    if (!repoData.success) {
      console.error("Failed to create aggregator repo", repoData.error);
      return;
    }

    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    if (!pubKey) {
      throw new Error("No public key found");
    }

    const aggregatorPayload = {
      taskId: TASK_ID,
      roundNumber,
      githubUsername: process.env.GITHUB_USERNAME,
      stakingKey,
      pubKey,
      action: "create-repo",
      issueUuid: repoData.data.branch_name,
      aggregatorUrl: repoData.data.fork_url,
    };
    const aggregatorSignature = await namespaceWrapper.payloadSigning(aggregatorPayload, stakingKeypair.secretKey);

    const aggregatorPodCallBody = {
      stakingKey,
      pubKey,
      signature: aggregatorSignature,
    };

    await orcaClient.podCall("add-aggregator-info", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(aggregatorPodCallBody),
    });

    const { isLeader, leaderNode } = await getLeaderNode({
      roundNumber,
      leaderNumber: 1,
      submitterPublicKey: stakingKey,
    });
    console.log({ isLeader, leaderNode });
    if (leaderNode === null) {
      return;
    }
    const payload = {
      taskId: TASK_ID,
      roundNumber,
      githubUsername: process.env.GITHUB_USERNAME,
      repoOwner: leaderNode,
      repoName: "builder-test",
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
      taskId: TASK_ID!,
      roundNumber,
      stakingKey,
      pubKey,
      stakingSignature,
      publicSignature,
      repoOwner: leaderNode,
      repoName: "builder-test",
      distributionList: {},
    };
    let podCallUrl;
    if (isLeader) {
      podCallUrl = `leader-task/${roundNumber}`;

      try {
        const distributionList = await getDistributionList(roundNumber - 3);
        if (!distributionList || Object.keys(distributionList).length === 0) {
          console.log("No distribution list available for this round, skipping leader task");
          return;
        }

        try {
          podCallBody.distributionList = distributionList;
        } catch (parseError) {
          console.error("Failed to parse distribution list:", parseError);
          console.log("Raw distribution list:", distributionList);
          console.log("Skipping leader task due to invalid distribution list");
          return;
        }
      } catch (distError) {
        console.error("Error fetching distribution list:", distError);
        console.log("Skipping leader task due to distribution list fetch error");
        return;
      }
    } else {
      podCallUrl = `worker-task/${roundNumber}`;
    }

    await orcaClient.podCall(podCallUrl, {
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
