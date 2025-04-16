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
  // @ts-ignore
  const { Octokit } = await import("@octokit/rest");
  octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
  });
}



async function createIssue(owner: string, repo: string, title: string, body: string) {
  if (!octokit) await initializeOctokit();
  try {
    const response = await octokit.rest.issues.create({
      owner: owner,
      repo: repo,
      title: title,
      body: body,
    });   
    // Check if status code is in the 2xx range (success)
    return response.data;
  } catch (error) {
    console.error("Error creating issue:", error);
    return null;
  }
}

async function starRepo(owner: string, repoName: string) : Promise<boolean> {
  if (!octokit) await initializeOctokit();
  try {
    const response = await octokit.rest.activity.starRepoForAuthenticatedUser({
      owner: owner,
      repo: repoName,
    });
    return response.status >= 200 && response.status < 300;
  } catch (error) {
    console.log("error", error);
    return false;
  }
}

async function checkStarred(owner: string, repoName: string, username: string) {
  if (!octokit) await initializeOctokit();
  try {
    const response = await octokit.rest.activity.listReposStarredByUser({
      username: username,
      sort: 'created',
      per_page: 100,
    });
    if (response.status != 200) {
      return true;
    }
    
    // Check if the target repo is in the list of starred repos
    const isStarred = response.data.some((repo: { owner: { login: string }, name: string }) => 
      repo.owner.login === owner && repo.name === repoName
    );
    return isStarred;
  } catch (error) {
    console.log("error", error);
    return true;
  }
}

async function followUser(owner: string) : Promise<boolean> {
  if (!octokit) await initializeOctokit();
  try {
    const response = await octokit.rest.users.follow({
      username: owner,
    });
    return response.status >= 200 && response.status < 300;
  } catch (error) {
    console.log("error", error);
    return false;
  }
}

async function checkFollowed(username: string, owner: string) {
  if (!octokit) await initializeOctokit();
  try {
    const response = await octokit.rest.users.checkFollowingForUser({
      username: username,
      target_user: owner,
    });
    if (response.status == 404) {
      // All other status code is not user's fault
      return false;
    }
    return true;
  } catch (error) {
    console.log("error", error);
    return true;
  }
}

async function checkRepoStatus(owner: string, repoName: string) {
  if (!octokit) await initializeOctokit();
  // Check if the repo exist and if it is public
  const response = await octokit.rest.repos.get({
    owner: owner,
    repo: repoName,
  });
  return response.status == 200;
}

async function getUserInfo() {
  if (!octokit) await initializeOctokit();
  try {
    const response = await octokit.rest.users.getAuthenticated();
    return {
      id: response.data.id,
      username: response.data.login
    };
  } catch (error) {
    console.error("Error getting user info:", error);
    return null;
  }
}

export { starRepo, createIssue, checkStarred, followUser, checkFollowed, checkRepoStatus, getUserInfo };