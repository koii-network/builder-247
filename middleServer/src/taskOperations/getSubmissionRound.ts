import { getTaskStateInfo } from "@_koii/create-task-cli";
import { Connection } from "@_koii/web3.js";



export async function getMaxSubmissionRound(taskId: string): Promise<number | null> {
    const connection = new Connection("https://mainnet.koii.network","confirmed");
    
    try {
        const taskStateInfo = await getTaskStateInfo(connection, taskId);
        const roundsInSubmission = Object.keys(taskStateInfo.submissions)
        const largestRound = Math.max(...roundsInSubmission.map(Number));
        return largestRound;
    } catch (error) {
        console.error('Error in getSubmissionRound', error);
        return 0;
    }
}




// async function main() {
//     const submissionRound = await getSubmissionRound("2xSoUfcPE9eTxmSvwjXA4myNK3T3HYpnUCgAV8szzeNn");
//     console.log(submissionRound);
// }

// main();