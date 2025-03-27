import "dotenv/config";
import dotenv from "dotenv";
dotenv.config();
export const taskID = process.env.TASK_ID || "tempSimulateTaskID";
export const RPCURL = "https://mainnet.koii.network";
export const defaultBountyMarkdownFile = process.env.DEFAULT_BOUNTY_MARKDOWN_FILE || "https://raw.githubusercontent.com/HermanL02/prometheus-swarm-bounties/master/README.md"

export const swarmBountyStatus = {
    INITIALIZED: "Initialized",
    COMPLETED: "Completed",
    FAILED: "Failed"
}