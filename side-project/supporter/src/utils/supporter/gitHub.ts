// Initialize Octokit with token
import dotenv from "dotenv";
dotenv.config();

// Debug: Print all environment variables
// console.log('All environment variables:', process.env);

let octokit: any;

async function initializeOctokit() {
  if (!process.env.GITHUB_TOKEN) {
    throw new Error('GitHub token is not configured. Please set GITHUB_TOKEN in your .env file');
  }
  // console.log("token", process.env.GITHUB_TOKEN);
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

async function checkStarred(owner: string, repoName: string, username: string) {
  if (!octokit) await initializeOctokit();
  try {
    const response = await octokit.rest.activity.listReposStarredByUser({
      username: username,
      sort: 'created',
      per_page: 100,
    });
    
    // Check if the target repo is in the list of starred repos
    const isStarred = response.data.some((repo: { owner: { login: string }, name: string }) => 
      repo.owner.login === owner && repo.name === repoName
    );
    return isStarred;
  } catch (error) {
    console.log("error", error);
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

async function checkFollowed(username: string, owner: string) {
  if (!octokit) await initializeOctokit();
  try {
    await octokit.rest.users.checkFollowingForUser({
      username: username,
      target_user: owner,
    });
    return true;
  } catch (error) {
    return false;
  }
}

export { starRepo, createIssue, checkStarred, followUser, checkFollowed };