import dotenv from "dotenv";
dotenv.config();

export const starAndFollowSupportRepo = "koii-network/StarAndFollowSupportRepo"
export const status = {
  ISSUE_CREATED_FAILED: "Issue created failed",
  FETCH_USER_INFO_FAILED: "Fetch user info failed",
  BIND_REPO_FAILED: "Bind repo failed",
  SUCCESS: "Success",
  FAILED: "Failed",
  GITHUB_CHECK_FAILED: "GitHub check failed",
  FOLLOW_FAILED: "Follow failed",
  STAR_FAILED: "Star failed",
  NO_DATA_FOR_THIS_ROUND: "No data for this round",
  FETCH_REPO_LIST_FAILED: "No or failed repo list",
}

export const errorMessage = {
  STAR_FAILED: "We couldn't star the repo. Please try again later.",
  FOLLOW_FAILED: "We couldn't follow the user. Please try again later.",
  FETCH_REPO_LIST_FAILED: "We couldn't fetch the repo list. Please try again later.",
  ISSUE_FAILED_TO_BE_SUMMARIZED: "We couldn't summarize this issue. Please try again later.",
  ISSUE_SUCCESSFULLY_SUMMARIZED: "The issue was successfully summarized.",
  NO_ISSUES_PENDING_TO_BE_SUMMARIZED: "There are no issues waiting to be summarized at this time.",
  ROUND_LESS_THAN_OR_EQUAL_TO_1: "This operation requires a round number greater than 1.",
  NO_ORCA_CLIENT: "The Orca client is not available.",
  NO_CHOSEN_AS_ISSUE_SUMMARIZER: "You haven't been selected as an issue summarizer.",
  UNKNOWN_ERROR: "An unexpected error occurred. Please try again later.",
  STAR_ISSUE_FAILED: "We couldn't star the issue. Please try again later.",
  GITHUB_CHECK_FAILED: "The GitHub check failed. Please verify your GitHub Key.",
  ANTHROPIC_API_KEY_INVALID: "The Anthropic API Key is not valid. Please check your API key.",
  ANTHROPIC_API_KEY_NO_CREDIT: "Your Anthropic API key has no remaining credits.",
  NO_DATA_FOR_THIS_ROUND: "There is no data available for this round.",
  ISSUE_FAILED_TO_ADD_PR_TO_SUMMARIZER_TODO: "We couldn't add the PR to the summarizer todo list.",
}

export const actionMessage = {
  ISSUE_FAILED_TO_BE_SUMMARIZED: "We couldn't summarize this issue. Please try again later.",
  ISSUE_SUCCESSFULLY_SUMMARIZED: "The issue was successfully summarized.",
  NO_ISSUES_PENDING_TO_BE_SUMMARIZED: "There are no issues waiting to be summarized at this time.",
  ROUND_LESS_THAN_OR_EQUAL_TO_1: "This operation requires a round number greater than 1.",
  NO_ORCA_CLIENT: "Please click Orca icon to connect your Orca Pod.",
  NO_CHOSEN_AS_ISSUE_SUMMARIZER: "You haven't been selected as an issue summarizer.",
  UNKNOWN_ERROR: "An unexpected error occurred. Please try again later.",
  STAR_ISSUE_FAILED: "We couldn't star the issue. Please try again later.",
  GITHUB_CHECK_FAILED: "Please go to the env variable page to update your GitHub Key.",
  ANTHROPIC_API_KEY_INVALID: "Please follow the guide under task description page to set up your Anthropic API key correctly.",
  ANTHROPIC_API_KEY_NO_CREDIT: "Please add credits to continue.",
  NO_DATA_FOR_THIS_ROUND: "There is no data available for this round.",
  ISSUE_FAILED_TO_ADD_PR_TO_SUMMARIZER_TODO: "We couldn't add the PR to the summarizer todo list. Please try again later.",
}
/*********************THE CONSTANTS THAT PROD/TEST ARE DIFFERENT *********************/
export const defaultBountyMarkdownFile = "https://raw.githubusercontent.com/koii-network/prometheus-swarm-bounties/master/README.md"

export const customReward = 400*10**9 // This should be in ROE! 

export const middleServerUrl = "https://ooww84kco0s0cs808w8cg804.dev.koii.network"