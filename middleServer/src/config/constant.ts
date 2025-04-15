import "dotenv/config";
import dotenv from "dotenv";
dotenv.config();
export const taskID = process.env.TASK_ID || "tempSimulateTaskID";
export const documentSummarizerTaskID = process.env.DOCUMENT_SUMMARIZER_TASK_ID || "H5CKDzSi2qWs7y7JGMX8sGvAZnWcUDx8k1mCMVWyJf1M";
export const RPCURL = "https://mainnet.koii.network";
export const defaultBountyMarkdownFile = process.env.DEFAULT_BOUNTY_MARKDOWN_FILE || "https://raw.githubusercontent.com/HermanL02/prometheus-swarm-bounties/master/README.md"
export const plannerTaskID = process.env.PLANNER_TASK_ID || "";
export const SUPPORTER_TASK_ID = process.env.SUPPORTER_TASK_ID || "";
export enum SwarmBountyStatus {
    COMPLETED = "completed",
    FAILED = "failed",
    IN_PROGRESS = "in-progress",
    // LOADING = "loading",
    ASSIGNED = "assigned",
    // FORKED = "forked"
    AUDITING = "auditing"
  }
export enum SwarmBountyType {
  DOCUMENT_SUMMARIZER = "document-summarizer",
  FIND_BUGS = "find-bugs",
  BUILD_FEATURE = "build-feature"
}