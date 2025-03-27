import SwarmBounty from "../models/SwarmBounties";
import { swarmBountyStatus } from "../constant";
import { connectToDatabase } from "../app";
import dotenv from "dotenv";

dotenv.config();

export async function updateStatus(githubUrl: string, status: string) {
    console.log("Updating status for", githubUrl, status);
    try {
        await connectToDatabase();
        const issue = await SwarmBounty.findOne({ githubUrl });
        if (!issue) {
            throw new Error("Issue not found");
        }
        issue.status = status;
        await issue.save();
    } catch (error) {
        console.error("Error:", error);
    }
}

// async function test() {
//     try {
//         await connectToDatabase();
//         await updateStatus("https://github.com/koii-network/koii-improvement-proposals", swarmBountyStatus.COMPLETED);
//         console.log("Status updated successfully");
//         process.exit(0);
//     } catch (error) {
//         console.error("Error:", error);
//         process.exit(1);
//     }
// }

// test(); 