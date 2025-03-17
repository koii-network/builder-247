import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getLeaderNode } from "../utils/leader";
import { filterIneligibleNodes } from "../utils/filterDistribution";

interface PodCallBody {
  taskId: string;
  roundNumber: number;
  stakingKey: string;
  pubKey: string;
  stakingSignature: string;
  publicSignature: string;
  repoOwner: string;
  repoName: string;
  distributionList: Record<string, number>;
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

    await orcaClient.podCall(`create-aggregator-repo/${roundNumber + 1}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // TODO: Change to dynamic repo owner and name by checking the middle server
      body: JSON.stringify({ taskId: TASK_ID, repoOwner: "koii-network", repoName: "builder-test" }),
    });

    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    if (!pubKey) {
      throw new Error("No public key found");
    }
    const {
      isLeader,
      leaderNode,
      stakingKey: leaderStakingKey,
    } = await getLeaderNode({
      roundNumber,
      leaderNumber: 1,
      submitterPublicKey: stakingKey,
    });
    console.log({ isLeader, leaderNode, leaderStakingKey });
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
      if (leaderStakingKey === null) {
        console.log("Leader staking key is null, skipping leader task");
        return;
      }

      try {
        console.log("Fetching distribution list for round", roundNumber, "with leader staking key", leaderStakingKey);
        const distributionList = await namespaceWrapper.getDistributionList(leaderStakingKey, roundNumber);

        if (!distributionList) {
          console.log("No distribution list available for this round, skipping leader task");
          return;
        }

        try {
          const parsedDistributionList = JSON.parse(distributionList);

          if (Object.keys(parsedDistributionList).length === 0) {
            console.log("Distribution list is empty, skipping leader task");
            return;
          }

          // Get submissions for this round to filter out ineligible ones
          const submissionsResponse = await orcaClient.podCall(`submission/${roundNumber}`);
          const submissions = submissionsResponse.data;

          if (!Array.isArray(submissions)) {
            console.log("No valid submissions data available, skipping leader task");
            return;
          }

          // Filter out ineligible nodes
          const filteredDistributionList = await filterIneligibleNodes(parsedDistributionList, submissions);

          if (Object.keys(filteredDistributionList).length === 0) {
            console.log("No eligible nodes in distribution list after filtering, skipping leader task");
            return;
          }

          podCallBody.distributionList = filteredDistributionList;
          console.log(
            "Successfully filtered distribution list. Eligible nodes:",
            Object.keys(filteredDistributionList).length,
          );
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
