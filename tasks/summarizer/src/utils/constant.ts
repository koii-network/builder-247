import dotenv from "dotenv";
dotenv.config();
export const defaultRepoOwner = process.env.DEFAULT_REPO_OWNER || "koii-network";

export const defaultBountyMarkdownFile = process.env.DEFAULT_BOUNTY_MARKDOWN_FILE || "https://raw.githubusercontent.com/koii-network/prometheus-swarm-bounties/master/README.md"