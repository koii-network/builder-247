// Initialize Octokit with token
import dotenv from "dotenv";
dotenv.config();
let octokit: any;

async function initializeOctokit() {
  const { Octokit } = await import("@octokit/rest");
  octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
  });
}

async function createIssue(owner: string, repo: string, title: string, body: string) {
  if (!octokit) await initializeOctokit();
  const response = await octokit.rest.issues.create({
    owner: owner,
    repo: repo,
    title: title,
    body: body,
  });   
  return response.status;
}

async function starRepo(owner: string, repoName: string) {
  if (!octokit) await initializeOctokit();
  const response = await octokit.rest.activity.starRepoForAuthenticatedUser({
    owner: owner,
    repo: repoName,
  });
  return response.status;
}

async function checkStarred(owner: string, repoName: string) {
  if (!octokit) await initializeOctokit();
  try {
    await octokit.rest.activity.checkRepoIsStarredByAuthenticatedUser({
      owner: owner,
      repo: repoName,
    });
    return true;
  } catch (error) {
    return false;
  }
}

async function followUser(owner: string) {
  if (!octokit) await initializeOctokit();
  const response = await octokit.rest.users.follow({
    username: owner,
  });
  return response.status === 204;
}

async function checkFollowed(owner: string) {
  if (!octokit) await initializeOctokit();
  try {
    await octokit.rest.users.checkFollowingForUser({
      username: owner,
      target_user: owner,
    });
    return true;
  } catch (error) {
    return false;
  }
}

export { starRepo, createIssue, checkStarred, followUser, checkFollowed };