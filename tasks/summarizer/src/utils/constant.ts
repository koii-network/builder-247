import dotenv from "dotenv";
dotenv.config();
export const defaultRepoOwner = process.env.DEFAULT_REPO_OWNER || "koii-network";

export const defaultBountyMarkdownFile = process.env.DEFAULT_BOUNTY_MARKDOWN_FILE || "https://raw.githubusercontent.com/HermanL02/prometheus-swarm-bounties/master/README.md"

export const status = {
  ISSUE_FAILED_TO_BE_SUMMARIZED: "Issue failed to be summarized",
  ISSUE_SUCCESSFULLY_SUMMARIZED: "Issue successfully summarized",
  NO_ISSUES_PENDING_TO_BE_SUMMARIZED: "No issues pending to be summarized",
  ROUND_LESS_THAN_OR_EQUAL_TO_1: "Round <= 1",
  NO_ORCA_CLIENT: "No orca client",
  NO_CHOSEN_AS_ISSUE_SUMMARIZER: "No chosen as issue summarizer",
}

export const customReward = 0.01; // This should be in ROE! 