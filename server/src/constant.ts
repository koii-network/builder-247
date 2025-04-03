import "dotenv/config";

export const taskIDs = process.env.TASK_IDS?.split(",").map((id) => id.trim()) || ["tempSimulateTaskID"];
export const RPCURL = "https://mainnet.koii.network";
