import dotenv from "dotenv";
dotenv.config();


export const status = {
  ISSUE_FAILED_TO_BE_SUMMARIZED: "Issue failed to be summarized",
  ISSUE_SUCCESSFULLY_SUMMARIZED: "Issue successfully summarized",
  NO_ISSUES_PENDING_TO_BE_SUMMARIZED: "No issues pending to be summarized",
  ROUND_LESS_THAN_OR_EQUAL_TO_1: "Round <= 1",
  // NO_ORCA_CLIENT: "No orca client",
  NO_CHOSEN_AS_ISSUE_SUMMARIZER: "No chosen as issue summarizer",
  UNKNOWN_ERROR: "Unknown error",
  STAR_ISSUE_FAILED: "Star issue failed",
  GITHUB_CHECK_FAILED: "GitHub check failed",
  ANTHROPIC_API_KEY_INVALID: "Anthropic API key invalid",
  ANTHROPIC_API_KEY_NO_CREDIT: "Anthropic API key has no credit",
  NO_DATA_FOR_THIS_ROUND: "No data for this round",
  ISSUE_FAILED_TO_ADD_PR_TO_SUMMARIZER_TODO: "Issue failed to add PR to summarizer todo",
}

/*********************THE CONSTANTS THAT PROD/TEST ARE DIFFERENT *********************/
export const defaultBountyMarkdownFile = "https://raw.githubusercontent.com/koii-network/prometheus-swarm-bounties/master/README.md"

export const customReward = 400*10**9 // This should be in ROE! 

export const middleServerUrl = "https://ooww84kco0s0cs808w8cg804.dev.koii.network"