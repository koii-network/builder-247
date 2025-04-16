import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { status, middleServerUrl } from "../utils/constant";
import { checkRepoStatus, createIssue, getUserInfo } from "../utils/supporter/gitHub";
import dotenv from "dotenv";
import { checkGitHub } from "../utils/githubCheck";
import { LogLevel } from "@_koii/namespace-wrapper/dist/types";
import { actionMessage } from "../utils/constant";
import { errorMessage } from "../utils/constant";
import { starAndFollowSupportRepo } from "../utils/constant";
import { starRepo, followUser } from "../utils/supporter/gitHub";

dotenv.config();

export async function task(roundNumber: number): Promise<void> {
    console.log("[TASK] Starting task execution for round:", roundNumber);
 
    if (!process.env.GITHUB_TOKEN) {
      console.log("[TASK] GitHub token is missing in environment variables");
      await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.GITHUB_CHECK_FAILED, actionMessage.GITHUB_CHECK_FAILED);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.GITHUB_CHECK_FAILED);
      return;
    }
    console.log("[TASK] GitHub token found, proceeding with validation");
    console.log("[TASK] GITHUB_TOKEN", process.env.GITHUB_TOKEN);
    const isGitHubValid = await checkGitHub(process.env.GITHUB_TOKEN!);
    console.log("[TASK] GitHub validation result:", isGitHubValid);
    
    if (!isGitHubValid) {
      console.log("[TASK] GitHub validation failed");
      await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.GITHUB_CHECK_FAILED, actionMessage.GITHUB_CHECK_FAILED);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.GITHUB_CHECK_FAILED);
      return;
    }
    console.log("[TASK] GitHub validation successful");

    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    if (!pubKey) {
      throw new Error("No public key found");
    }

    /******************REQUEST TO BIND REPO TO THE TASK ******************/
    const issueCreateData = await createIssue(starAndFollowSupportRepo.split('/')[0], starAndFollowSupportRepo.split('/')[1], `Support`, JSON.stringify({stakingKey: stakingKey}));
    if (!issueCreateData) {
      // await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.ISSUE_FAILED_TO_BE_SUMMARIZED, actionMessage.ISSUE_FAILED_TO_BE_SUMMARIZED);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.ISSUE_CREATED_FAILED);
      return;
    }
    const issueNumber = issueCreateData.number;
    const userInfo = await getUserInfo();
    if (!userInfo) {
      // await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.GITHUB_CHECK_FAILED, actionMessage.GITHUB_CHECK_FAILED);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.FETCH_USER_INFO_FAILED);
      return;
    }
    const bindStatusInDB = await namespaceWrapper.storeGet(`bind-status-${userInfo.id}`);
    if (!bindStatusInDB) {
      const bindRepo = await fetch(`${middleServerUrl}/api/supporter/bind-key-to-github`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({stakingKey: stakingKey, githubId: userInfo.id, githubUsername: userInfo.username, issueNumber: issueNumber}),
      });
      const bindRepoJson = await bindRepo.json();
      if (bindRepoJson.statuscode !== 200) {
        await namespaceWrapper.storeSet(`result-${roundNumber}`, status.BIND_REPO_FAILED);
        return;
      } else{
        await namespaceWrapper.storeSet(`bind-status-${userInfo.id}`, status.SUCCESS);
      }
    }


    /****************** All issues need to be starred ******************/

    const signature = await namespaceWrapper.payloadSigning(
      {
        roundNumber: roundNumber,
        action: "fetch",
        stakingKey: stakingKey
      },
      stakingKeypair.secretKey,
    );
    const fetchRepoList = await fetch(`${middleServerUrl}/api/supporter/fetch-repo-list`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        stakingKey: stakingKey,
        signature: signature,
      }),
    });
    const fetchRepoListJson = await fetchRepoList.json();
    if (fetchRepoListJson.statuscode !== 200) {
      // await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.FETCH_REPO_LIST_FAILED, actionMessage.FETCH_REPO_LIST_FAILED);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.FETCH_REPO_LIST_FAILED);
      return;
    }
    const repoUrlList = fetchRepoListJson.data.pendingRepos;
    const repoList = repoUrlList.map((repo: string) => {
      const [,, , owner, repoName] = repo.split("/");
      return `${owner}/${repoName}`;
    });
    
    /****************** Create a issue to bind the repo to the task ******************/
    try {
      for (const repo of repoList) {
        const [owner, repoName] = repo.split("/");
        // Check if already done
        const isDone = await namespaceWrapper.storeGet(`repo-${repo}`);
        if (isDone === status.SUCCESS) {
          continue;
        }
        const isRepoExist = await checkRepoStatus(owner, repoName);
        if (!isRepoExist) {
          continue;
        }
        const isStarred = await starRepo(owner, repoName);
        const isFollowed = await followUser(owner);
        console.log(`${repo} starred: ${isStarred}, followed: ${isFollowed}`);
      }
    } catch (error) {
      console.error("Error starring repos:", error);
    }

    await namespaceWrapper.storeSet(`result-${roundNumber}`, status.SUCCESS);
}
