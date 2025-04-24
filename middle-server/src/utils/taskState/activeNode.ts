import { getTaskStateInfo } from "@_koii/create-task-cli";
import { Connection } from "@_koii/web3.js";

export async function getLastRoundValueLength(taskId: string): Promise<number> {
    const connection = new Connection("https://mainnet.koii.network", "confirmed");
    const taskState = await getTaskStateInfo(connection, taskId);
    const roundKeys = Object.keys(taskState.submissions);
    const lastRound = Math.max(...roundKeys.map(Number));
    const lastRoundValue = taskState.submissions[(lastRound-1).toString()];
    if (!lastRoundValue) {
        throw new Error("Last round value is undefined or null");
    }
    return Object.keys(lastRoundValue).length;
}

