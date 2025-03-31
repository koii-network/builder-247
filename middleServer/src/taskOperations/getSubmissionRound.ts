import { getTaskStateInfo } from "@_koii/create-task-cli";
import { Connection, PublicKey } from "@_koii/web3.js";

export async function getMaxSubmissionRound(taskId: string): Promise<number | null> {
    if (!taskId) {
        console.error('Task ID is required');
        return null;
    }

    try {
        // Validate that taskId is a valid Solana public key
        new PublicKey(taskId);
    } catch (error) {
        console.error('Invalid task ID format:', error);
        return null;
    }

    const connection = new Connection("https://mainnet.koii.network", "confirmed");
    
    try {
        const taskStateInfo = await getTaskStateInfo(connection, taskId);
        if (!taskStateInfo || !taskStateInfo.submissions) {
            console.error('No task state info found for task:', taskId);
            return null;
        }
        const roundsInSubmission = Object.keys(taskStateInfo.submissions);
        if (roundsInSubmission.length === 0) {
            console.error('No submission rounds found for task:', taskId);
            return null;
        }
        const largestRound = Math.max(...roundsInSubmission.map(Number));
        // Return the largest round, even if it's 0
        return largestRound;
    } catch (error) {
        console.error('Error in getMaxSubmissionRound:', error);
        return null;
    }
}


export async function getCurrentRound(taskId: string): Promise<number | null> {
    const connection = new Connection("https://mainnet.koii.network", "confirmed");
    const taskStateInfo = await getTaskStateInfo(connection, taskId);
    const currentSlot = await connection.getSlot();
    console.log("currentSlot", currentSlot);
    console.log("taskStateInfo.starting_slot", taskStateInfo.starting_slot);
    const currentRound = Math.floor(
        (currentSlot - taskStateInfo.starting_slot) / taskStateInfo.round_time,
      );
    return currentRound;
}

// async function main() {
//         const submissionRound = await getCurrentRound("2xSoUfcPE9eTxmSvwjXA4myNK3T3HYpnUCgAV8szzeNn");
//         console.log(submissionRound);
// }

// main();