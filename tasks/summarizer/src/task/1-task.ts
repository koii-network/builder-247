import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getRandomNodes } from "../utils/leader";
import { getExistingIssues, getInitializedDocumentSummarizeIssues } from "../utils/existingIssues";
import { status } from "../utils/constant";
import dotenv from "dotenv";

dotenv.config();


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

    if (orcaClient && roundNumber == 0) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ROUND_LESS_THAN_OR_EQUAL_TO_1);
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
    /****************** All issues need to be starred ******************/

    const existingIssues = await getExistingIssues();
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

    
    const initializedDocumentSummarizeIssues = await getInitializedDocumentSummarizeIssues(existingIssues);
    console.log("Initialized document summarize issues:", initializedDocumentSummarizeIssues);
    if (initializedDocumentSummarizeIssues.length == 0) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_ISSUES_PENDING_TO_BE_SUMMARIZED);
      return;
    } 
    const randomNodes = await getRandomNodes(roundNumber, initializedDocumentSummarizeIssues.length);
    if (randomNodes.length === 0) {
      return;
    }
    console.log("Returned random nodes:", randomNodes);
    // Check my position in the list
    const myPosition = randomNodes.indexOf(stakingKey);
    if (myPosition === -1) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_CHOSEN_AS_ISSUE_SUMMARIZER);
      return;
    }
    const repoUrl = initializedDocumentSummarizeIssues[myPosition].githubUrl;

    console.log("repoUrl: ", repoUrl);
    console.log("calling podcall with repoUrl: ", repoUrl);
    const jsonBody = {
      taskId: TASK_ID,
      round_number: String(roundNumber),
      repo_url: repoUrl,
    };
    console.log("jsonBody: ", jsonBody);
    const response = await orcaClient.podCall(`repo_summary/${roundNumber}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(jsonBody),
    });
    console.log("response: ", response);
    if (response.status === 200) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_SUCCESSFULLY_SUMMARIZED);
    } else {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_BE_SUMMARIZED);
    }

    // TODO: TRIGGER CHANGE THE ISSUE STATUS HERE
    // WHY HERE? Because the distribution list happening the same time, so to avoid the issue is closed before the distribution list is generated
    
  } catch (error) {
    console.error("EXECUTE TASK ERROR:", error);
  }
}
