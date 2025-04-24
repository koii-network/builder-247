import "dotenv/config";
export const SUPPORTER_TASK_ID = process.env.SUPPORTER_TASK_ID || "";
export const documentSummarizerTaskID =
  process.env.DOCUMENT_SUMMARIZER_TASK_ID || "H5CKDzSi2qWs7y7JGMX8sGvAZnWcUDx8k1mCMVWyJf1M";
export const RPCURL = "https://mainnet.koii.network";
export const defaultBountyMarkdownFile =
  process.env.DEFAULT_BOUNTY_MARKDOWN_FILE ||
  "https://raw.githubusercontent.com/HermanL02/prometheus-swarm-bounties/master/README.md";
export const plannerTaskID = process.env.PLANNER_TASK_ID || "";

import { DocumentationStatus } from "../models/Documentation";
export enum SwarmBountyStatus {
  COMPLETED = "completed",
  FAILED = "failed",
  IN_PROGRESS = "in-progress",
  ASSIGNED = "assigned",
  AUDITING = "auditing",
}
// export const SwarmBountyStatusDocumentationStatusMapping = {
//   [DocumentationStatus.DONE]: SwarmBountyStatus.COMPLETED,
//   [DocumentationStatus.FAILED]: SwarmBountyStatus.FAILED,
//   [DocumentationStatus.IN_PROGRESS]: SwarmBountyStatus.IN_PROGRESS,
//   [DocumentationStatus.IN_PROGRESS]: SwarmBountyStatus.ASSIGNED,
//   [DocumentationStatus.AUDITING]: SwarmBountyStatus.AUDITING,
// }
export enum SwarmBountyType {
  DOCUMENT_SUMMARIZER = "document-summarizer",
  FIND_BUGS = "find-bugs",
  BUILD_FEATURE = "build-feature",
}
export const taskIDs = process.env.TASK_IDS?.split(",").map((id) => id.trim()) || ["tempSimulateTaskID"];
export const BYPASS_TASK_STATE_CHECK = process.env.NODE_ENV === "development";
