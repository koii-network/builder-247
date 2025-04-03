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
  if (roundNumber >= 3) {
    const triggerFetchAuditResult = await fetch(`${middleServerUrl}/api/summarizer/trigger-fetch-audit-result`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ taskId: TASK_ID, round: roundNumber - 3 })
    });
    console.log(`Trigger fetch audit result for round ${roundNumber - 3}. Result is ${triggerFetchAuditResult.status}.`);
  }
  console.log(`EXECUTE TASK FOR ROUND ${roundNumber}`);
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
    console.log("Existing issues:", existingIssues);
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

    console.log(`Making Request to Middle Server with taskId: ${TASK_ID} and round: ${roundNumber}`);
    const requiredWorkResponse = await fetch(`${middleServerUrl}/api/summarizer/fetch-summarizer-todo`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ signature: signature, stakingKey: stakingKey }),
    });
    const data = await requiredWorkResponse.json();
    console.log("data: ", data);
    
    const jsonBody = {
      taskId: TASK_ID,
      round_number: String(roundNumber),
      repo_url: `https://github.com/${data.repo_owner}/${data.repo_name}`,
    };
    console.log("jsonBody: ", jsonBody);
    try {
      const repoSummaryResponse = await orcaClient.podCall(`repo_summary/${roundNumber}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonBody),
      });
      console.log("repoSummaryResponse: ", repoSummaryResponse);
      if (repoSummaryResponse.status === 200) {
        try{
          const signature = await namespaceWrapper.payloadSigning(
            {
              taskId: TASK_ID,
              action: "add",
              roundNumber: roundNumber,
              prUrl: repoSummaryResponse.data?.result?.data?.prUrl,
              stakingKey: stakingKey
            },
            stakingKeypair.secretKey,
          );
          const response = await fetch(`${middleServerUrl}/api/summarizer/add-pr-to-summarizer-todo`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ signature: signature, stakingKey: stakingKey }),
          });
          console.log("response: ", response);
        }catch(error){
          await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_BE_SUMMARIZED);
          console.error("Error adding PR to summarizer todo:", error);
        }
        await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_SUCCESSFULLY_SUMMARIZED);
      } else {
        await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_BE_SUMMARIZED);
      }
    } catch (error) {
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_FAILED_TO_BE_SUMMARIZED);
      console.error("EXECUTE TASK ERROR:", error);
    }
  } catch (error) {
    await namespaceWrapper.storeSet(`result-${roundNumber}`, status.UNKNOWN_ERROR);
    console.error("EXECUTE TASK ERROR:", error);
  }
}
