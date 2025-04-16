import { getOrcaClient } from "@_koii/task-manager/extensions";
import { middleServerUrl, status } from "../utils/constant";
import { checkStarred, checkFollowed, checkRepoStatus } from "../utils/supporter/gitHub";
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
    if (cid !== status.SUCCESS) {
      if (Object.values(status).includes(cid)) {
        return true;
      }else{
        return false;
      }
    }



    const checkSummarizerResponse = await fetch(`${middleServerUrl}/api/supporter/check-request`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ 
        stakingKey: submitterKey,
      }),
    });


    const checkSummarizerJSON = await checkSummarizerResponse.json();
    console.log(`[AUDIT] Summarizer check response:`, checkSummarizerJSON);
    const {pendingRepos, githubUsername} = checkSummarizerJSON.data;
    const repoList = pendingRepos.map((repo: string) => {
      const [,, , owner, repoName] = repo.split("/");
      return `${owner}/${repoName}`;
    });
    // Loop 
    for (const repo of repoList) {
      const repoName = repo.split('/')[1];
      const owner = repo.split('/')[0];
      // Check if this repo is starred and followed
      const isRepoExist = await checkRepoStatus(owner, repoName);
      if (isRepoExist) {
        const isStarred = await checkStarred(githubUsername, owner, repoName);
        const isFollowed = await checkFollowed(githubUsername,  owner);
        if (!isStarred || !isFollowed) {
          return false;
        }
      }else{
        // DO NOTHING HERE! BECAUSE IT IS NOT A REPO, MEANS NOT TASK NODE"S FAULT
      }


    }
    return true;
  } catch (error) {
    console.error("[AUDIT] Error auditing submission:", error);

    // When Error---NO RETURN;
    // return true;
  }
}


