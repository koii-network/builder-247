
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getRandomNodes } from "../utils/leader";
import { getExistingIssues } from "../utils/existingIssues";
import { status, middleServerUrl } from "../utils/constant";
import { createIssue } from "../utils/supporter/gitHub";
import dotenv from "dotenv";
import { checkAnthropicAPIKey, isValidAnthropicApiKey } from "../utils/anthropicCheck";
import { checkGitHub } from "../utils/githubCheck";
import { LogLevel } from "@_koii/namespace-wrapper/dist/types";
import { actionMessage } from "../utils/constant";
import { errorMessage } from "../utils/constant";
import { starAndFollowSupportRepo } from "../utils/constant";
import { starRepo, followUser } from "../utils/supporter/gitHub";


dotenv.config();


export async function task(roundNumber: number): Promise<void> {
 
    if (!process.env.GITHUB_USERNAME || !process.env.GITHUB_TOKEN) {
      await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.GITHUB_CHECK_FAILED, actionMessage.GITHUB_CHECK_FAILED);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.GITHUB_CHECK_FAILED);
      return;
    }
    const isGitHubValid = await checkGitHub(process.env.GITHUB_USERNAME!, process.env.GITHUB_TOKEN!);
    if (!isGitHubValid) {
      await namespaceWrapper.logMessage(LogLevel.Error, errorMessage.GITHUB_CHECK_FAILED, actionMessage.GITHUB_CHECK_FAILED);
      await namespaceWrapper.storeSet(`result-${roundNumber}`, status.GITHUB_CHECK_FAILED);
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
    const repoUrlList = fetchRepoListJson.data.repoList;
    const repoList = repoUrlList.map((repo: string) => {
      const [,, , owner, repoName] = repo.split("/");
      return `${owner}/${repoName}`;
    });
    
    /****************** Create a issue to bind the repo to the task ******************/
    try {
      for (const repo of repoList) {
        const [owner, repoName] = repo.split("/");
        await starRepo(owner, repoName);
        await followUser(owner);
      }
    } catch (error) {
      console.error("Error starring repos:", error);
    }

    const gitHubVerificationJson = {stakingKey}
    const response = await createIssue(starAndFollowSupportRepo.split('/')[0], starAndFollowSupportRepo.split('/')[1], `Support repo for round ${roundNumber}`, JSON.stringify(gitHubVerificationJson));

    await namespaceWrapper.storeSet(`result-${roundNumber}`, status.SUCCESS);
}
