import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getLeaderNode, getRandomNodes } from "../utils/leader";
import { getDistributionList } from "../utils/distributionList";
import { getExistingIssues, getInitializedDocumentSummarizeIssues } from "../utils/existingIssues";
import { status } from "../utils/constant";
import dotenv from "dotenv";

dotenv.config();

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
    // TODO BEFORE PRODUCTION: REMOVE THIS COMMENTS
    // if (orcaClient && roundNumber <= 1) {
    //   await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ROUND_LESS_THAN_OR_EQUAL_TO_1);
    //   return;
    // }
    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    if (!pubKey) {
      throw new Error("No public key found");
    }
    /****************** All issues need to be starred ******************/
    const existingIssues = [{githubUrl: "https://github.com/koii-network/koii-docs"}];
    console.log("Existing issues:", existingIssues);
    const githubUrls = existingIssues.map((issue) => issue.githubUrl);
    await orcaClient.podCall(`star/${roundNumber}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ taskId: TASK_ID, round_number: String(roundNumber), github_urls: githubUrls }),
    });
    /****************** All these issues need to be generate a markdown file ******************/
    const initializedDocumentSummarizeIssues = [{githubUrl: "https://github.com/koii-network/koii-docs"}];
    console.log("Initialized document summarize issues:", initializedDocumentSummarizeIssues);
    if (initializedDocumentSummarizeIssues.length == 0) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_ISSUES_PENDING_TO_BE_SUMMARIZED);
      return;
    } else {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUES_PENDING_TO_BE_SUMMARIZED);
    }
    const randomNodes = [stakingKey];
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
      body: JSON.stringify({ taskId: TASK_ID, round_number: String(roundNumber), repo_url: repoUrl }),
    });
  } catch (error) {
    console.error("EXECUTE TASK ERROR:", error);
  }
}
