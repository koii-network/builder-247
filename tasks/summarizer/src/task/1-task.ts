import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getLeaderNode, getRandomNodes } from "../utils/leader";
import { getDistributionList } from "../utils/distributionList";
import { getExistingIssues, getInitializedDocumentSummarizeIssues } from "../utils/existingIssues";
import { status } from "../utils/constant";

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
    if (!orcaClient) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_ORCA_CLIENT);
      return;
    }
    if (orcaClient && roundNumber <= 1) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ROUND_LESS_THAN_OR_EQUAL_TO_1);
      return;
    }
    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    // const pubKey = await namespaceWrapper.getMainAccountPubkey();
    // if (!pubKey) {
    //   throw new Error("No public key found");
    // }
    // All these issues need to be starred
    const existingIssues = await getExistingIssues();
    const githubUrls = existingIssues.map((issue) => issue.githubUrl);
    await orcaClient.podCall(`star/${roundNumber}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ taskId: TASK_ID, round_number: roundNumber, github_urls: githubUrls }),
    });
    // All these issues need to be generate a markdown file
    const initializedDocumentSummarizeIssues = await getInitializedDocumentSummarizeIssues();
    if (initializedDocumentSummarizeIssues.length == 0) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_ISSUES_PENDING_TO_BE_SUMMARIZED);
      return;
    } else {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUES_PENDING_TO_BE_SUMMARIZED);
    }
 
    const randomNodes = await getRandomNodes(roundNumber, stakingKey, initializedDocumentSummarizeIssues.length);
    if (randomNodes.length === 0) {
      return;
    }
    // Check my position in the list
    const myPosition = randomNodes.indexOf(stakingKey);
    if (myPosition === -1) {
      return;
    }
    const repoUrl = initializedDocumentSummarizeIssues[myPosition].githubUrl;
    await orcaClient.podCall(`repo_summary/${roundNumber}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // TODO: Change to dynamic repo owner and name by checking the middle server
      body: JSON.stringify({ taskId: TASK_ID, round_number: roundNumber, repo_url: repoUrl }),
    });
    // const payload = {
    //   taskId: TASK_ID,
    //   roundNumber,`
    //   githubUsername: process.env.GITHUB_USERNAME,
    //   repoOwner: leaderNode,
    //   repoName: "builder-test",
    //   stakingKey,
    //   pubKey,
    //   action: "task",
    // };
    // const stakingSignature = await namespaceWrapper.payloadSigning(payload, stakingKeypair.secretKey);
    // const publicSignature = await namespaceWrapper.payloadSigning(payload);
    // if (!stakingSignature || !publicSignature) {
    //   throw new Error("Signature generation failed");
    // }

    // const podCallBody: PodCallBody = {
    //   taskId: TASK_ID!,
    //   roundNumber,
    //   stakingKey,
    //   pubKey,
    //   stakingSignature,
    //   publicSignature,
    //   repoOwner: leaderNode,
    //   repoName: "builder-test",
    //   distributionList: {},
    // };
    // let podCallUrl;
    // if (isLeader) {
    //   podCallUrl = `leader-task/${roundNumber}`;

    //   try {
    //     const distributionList = await getDistributionList(roundNumber - 3);
    //     if (!distributionList || Object.keys(distributionList).length === 0) {
    //       console.log("No distribution list available for this round, skipping leader task");
    //       return;
    //     }

    //     try {
    //       podCallBody.distributionList = distributionList;
    //     } catch (parseError) {
    //       console.error("Failed to parse distribution list:", parseError);
    //       console.log("Raw distribution list:", distributionList);
    //       console.log("Skipping leader task due to invalid distribution list");
    //       return;
    //     }
    //   } catch (distError) {
    //     console.error("Error fetching distribution list:", distError);
    //     console.log("Skipping leader task due to distribution list fetch error");
    //     return;
    //   }
    // } else {
    //   podCallUrl = `worker-task/${roundNumber}`;
    // }

    // await orcaClient.podCall(podCallUrl, {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json",
    //   },
    //   body: JSON.stringify(podCallBody),
    // });
  } catch (error) {
    console.error("EXECUTE TASK ERROR:", error);
  }
}
