import dotenv from "dotenv";
dotenv.config();
export const defaultRepoOwner = process.env.DEFAULT_REPO_OWNER || "koii-network";

export const defaultBountyMarkdownFile = process.env.DEFAULT_BOUNTY_MARKDOWN_FILE || "https://raw.githubusercontent.com/koii-network/prometheus-swarm-bounties/master/README.md"

export const status = {
  ISSUES_PENDING_TO_BE_SUMMARIZED: "Issues pending to be summarized",
  NO_ISSUES_PENDING_TO_BE_SUMMARIZED: "No issues pending to be summarized",
  ROUND_LESS_THAN_OR_EQUAL_TO_1: "Round <= 1",
  NO_ORCA_CLIENT: "No orca client",
}