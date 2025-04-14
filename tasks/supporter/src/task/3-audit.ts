import { getOrcaClient } from "@_koii/task-manager/extensions";
import { middleServerUrl, status } from "../utils/constant";
import { checkStarred, checkFollowed } from "../utils/supporter/gitHub";
// import { status } from '../utils/constant'
export async function audit(cid: string, roundNumber: number, submitterKey: string): Promise<boolean | void> {
  /**
   * Audit a submission
   * This function should return true if the submission is correct, false otherwise
   * The default implementation retrieves the proofs from IPFS
   * and sends them to your container for auditing
   */

  try {
    // Check if the cid is one of the status
    if (Object.values(status).includes(cid)) {
      // This returns a dummy true
      return true;
    }


    const checkSummarizerResponse = await fetch(`${middleServerUrl}/api/summarizer/check-summarizer`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ 
        stakingKey: submitterKey, 
        roundNumber
      }),
    });


    const checkSummarizerJSON = await checkSummarizerResponse.json();
    console.log(`[AUDIT] Summarizer check response:`, checkSummarizerJSON);
    const {repoList, GitHubUsername} = checkSummarizerJSON.data;
    // Loop 
    for (const repo of checkSummarizerJSON.data) {
      const repoName = repo.split('/')[1];
      const owner = repo.split('/')[0];
      // Check if this repo is starred and followed
      const isStarred = await checkStarred(GitHubUsername, owner, repoName);
      const isFollowed = await checkFollowed(GitHubUsername, owner);
      if (!isStarred || !isFollowed) {
        return false;
      }
    }
    return true;
  } catch (error) {
    console.error("[AUDIT] Error auditing submission:", error);

    // When Error---NO RETURN;
    // return true;
  }
}


