import "dotenv/config";

export const taskID = process.env.TASK_ID || "tempSimulateTaskID";
export const RPCURL = "https://mainnet.koii.network";

export const taskIDs = process.env.TASK_IDS?.split(", ") || [];
