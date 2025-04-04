import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getRandomNodes } from "../utils/leader";
import { getExistingIssues } from "../utils/existingIssues";
import { status, middleServerUrl } from "../utils/constant";
import dotenv from "dotenv";

dotenv.config();


export async function task(roundNumber: number): Promise<void> {
  /**
   * Run your task and store the proofs to be submitted for auditing
   * It is expected you will store the proofs in your container
   * The submission of the proofs is done in the submission function
   */
  // FORCE TO PAUSE 30 SECONDS
// No submission on Round 0 so no need to trigger fetch audit result before round 3
// Changed from 3 to 4 to have more time
  if (roundNumber >= 4) {
    const triggerFetchAuditResult = await fetch(`${middleServerUrl}/api/summarizer/trigger-fetch-audit-result`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ taskId: TASK_ID, round: roundNumber - 4 })
    });
    console.log(`[TASK] Trigger fetch audit result for round ${roundNumber - 3}. Result is ${triggerFetchAuditResult.status}.`);
  }
  console.log(`[TASK] EXECUTE TASK FOR ROUND ${roundNumber}`);
  try {
    const orcaClient = await getOrcaClient();
    if (!orcaClient) {
      // await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_ORCA_CLIENT);
      return;
    }

    // if (orcaClient) {
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

    const existingIssues = await getExistingIssues();
    const githubUrls = existingIssues.map((issue) => issue.githubUrl);
    try {
      await orcaClient.podCall(`star/${roundNumber}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ taskId: TASK_ID, round_number: String(roundNumber), github_urls: githubUrls }),
      });
    } catch (error) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.STAR_ISSUE_FAILED);
      console.error("Error starring issues:", error);
    }
    /****************** All these issues need to be generate a markdown file ******************/

    const signature = await namespaceWrapper.payloadSigning(
      {
        taskId: TASK_ID,
        roundNumber: roundNumber,
        action: "fetch",
        githubUsername: stakingKey,
        stakingKey: stakingKey
      },
      stakingKeypair.secretKey,
    );

    // const initializedDocumentSummarizeIssues = await getInitializedDocumentSummarizeIssues(existingIssues);

    console.log(`[TASK] Making Request to Middle Server with taskId: ${TASK_ID} and round: ${roundNumber}`);
    const requiredWorkResponse = await fetch(`${middleServerUrl}/api/summarizer/fetch-summarizer-todo`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ signature: signature, stakingKey: stakingKey }),
    });
    // check if the response is 200
    if (requiredWorkResponse.status !== 200) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.NO_ISSUES_PENDING_TO_BE_SUMMARIZED);
      return;
    }
    const requiredWorkResponseData = await requiredWorkResponse.json();
    console.log("[TASK] requiredWorkResponseData: ", requiredWorkResponseData);
    
    const jsonBody = {
      taskId: TASK_ID,
      round_number: String(roundNumber),
      repo_url: `https://github.com/${requiredWorkResponseData.data.repo_owner}/${requiredWorkResponseData.data.repo_name}`,
    };
    console.log("[TASK] jsonBody: ", jsonBody);
    try {
      const repoSummaryResponse = await orcaClient.podCall(`repo_summary/${roundNumber}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonBody),
      });
      console.log("[TASK] repoSummaryResponse: ", repoSummaryResponse);
      console.log("[TASK] repoSummaryResponse.data.result.data ", repoSummaryResponse.data.result.data);
      const payload = {
        taskId: TASK_ID,
        action: "add",
        roundNumber: roundNumber,
        prUrl: repoSummaryResponse.data.result.data.pr_url,
        stakingKey: stakingKey
      }
      console.log("[TASK] Signing payload: ", payload);
      if (repoSummaryResponse.status === 200) {
        try{
          const signature = await namespaceWrapper.payloadSigning(
            payload,
            stakingKeypair.secretKey,
          );
          console.log("[TASK] signature: ", signature);
          const addPrToSummarizerTodoResponse = await fetch(`${middleServerUrl}/api/summarizer/add-pr-to-summarizer-todo`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ signature: signature, stakingKey: stakingKey }),
          });
          console.log("[TASK] addPrToSummarizerTodoResponse: ", addPrToSummarizerTodoResponse);
        }catch(error){
          await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_BE_SUMMARIZED);
          console.error("[TASK] Error adding PR to summarizer todo:", error);
        }
        await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_SUCCESSFULLY_SUMMARIZED);
      } else {
        await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_BE_SUMMARIZED);
      }
    } catch (error) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_BE_SUMMARIZED);
      console.error("[TASK] EXECUTE TASK ERROR:", error);
    }
  } catch (error) {
    await namespaceWrapper.storeSet(`result-${roundNumber}`, status.UNKNOWN_ERROR);
    console.error("[TASK] EXECUTE TASK ERROR:", error);
  }
}
