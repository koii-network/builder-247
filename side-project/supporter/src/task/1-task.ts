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
      console.log("[TASK] Issue creation failed");
      return;
    }
    const issueNumber = issueCreateData.number;
    // Try to get cached user info first
    const cachedUserInfo = await namespaceWrapper.storeGet('user-info');
    let userInfo;
    if (cachedUserInfo) {
      console.log("[TASK] Using cached user info");
      userInfo = JSON.parse(cachedUserInfo);
    } else {
      console.log("[TASK] Fetching fresh user info from GitHub");
      userInfo = await getUserInfo();
      if (userInfo) {
        // Cache the user info for future use
        await namespaceWrapper.storeSet('user-info', JSON.stringify(userInfo));
      }
    }
    if (!userInfo) {
      // await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.GITHUB_CHECK_FAILED, actionMessage.GITHUB_CHECK_FAILED);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.FETCH_USER_INFO_FAILED);
      console.log("[TASK] Fetch user info failed");
      return;
    }
    const bindStatusInDB = await namespaceWrapper.storeGet(`bind-status-${userInfo.id}`);
    if (!bindStatusInDB) {
      console.log("[TASK] Bind status in DB not found, proceeding with binding");
      try {
        const bindRepo = await fetch(`${middleServerUrl}/api/supporter/bind-key-to-github`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({stakingKey: stakingKey, githubId: userInfo.id, githubUsername: userInfo.username, issueNumber: issueNumber}),
        });
        const bindRepoJson = await bindRepo.json();
        if (bindRepoJson.statuscode >= 200 && bindRepoJson.statuscode < 300) {
          await namespaceWrapper.storeSet(`bind-status-${userInfo.id}`, status.SUCCESS);
        } else {
          await namespaceWrapper.storeSet(`result-${roundNumber}`, status.BIND_REPO_FAILED);
          return;
        }
      } catch (error) {
        console.error("[TASK] Error binding repo:", error);
        await namespaceWrapper.storeSet(`result-${roundNumber}`, status.BIND_REPO_FAILED);
        return;
      }
    } else {
      console.log("[TASK] Bind status already exists in DB, skipping bind request");
    }

    console.log("[TASK] Starting repository processing section");
    /****************** All issues need to be starred ******************/

    console.log("[TASK] Creating signature for repo list fetch");
    try {
      const signature = await namespaceWrapper.payloadSigning(
        {
          roundNumber: roundNumber,
          action: "fetch",
          stakingKey: stakingKey,
          taskId: TASK_ID,
        },
        stakingKeypair.secretKey,
      );
      console.log("[TASK] Signature created successfully");
      
      let repoList: string[] = [];
      console.log("[TASK] Fetching repository list from middle server");
      try {
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
        console.log("[TASK] Repository list fetch response status:", fetchRepoList.status);
        const fetchRepoListJson = await fetchRepoList.json();
        if (fetchRepoListJson.statuscode !== 200) {
          console.log("[TASK] Failed to fetch repository list, status code:", fetchRepoListJson.statuscode);
          await namespaceWrapper.storeSet(`result-${roundNumber}`, status.FETCH_REPO_LIST_FAILED);
          return;
        }
        console.log("[TASK] Successfully fetched repository list");
        const repoUrlList = fetchRepoListJson.data.pendingRepos;
        console.log("[TASK] Repo url list:", repoUrlList);
        repoList = repoUrlList.map((repo: string) => {
          const [,, , owner, repoName] = repo.split("/");
          return `${owner}/${repoName}`;
        });
        console.log("[TASK] Processed repo list:", repoList);
      } catch (error) {
        console.error("[TASK] Error fetching repo list:", error);
        await namespaceWrapper.storeSet(`result-${roundNumber}`, status.FETCH_REPO_LIST_FAILED);
        return;
      }
    } catch (error) {
      console.error("[TASK] Error starring repos:", error);
    }

    await namespaceWrapper.storeSet(`result-${roundNumber}`, status.SUCCESS);
}
