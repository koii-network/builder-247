import { DocumentationModel } from "../../models/Documentation";
import { SwarmBountyStatus, SwarmBountyType } from "../../config/constant";
import { getSwarmBounty } from "../../utils/prometheus/api";
import dotenv from "dotenv";
dotenv.config();
// import SwarmBounty from "../../models/SwarmBounties";
export async function syncDB() {
    // Get all feature bounties
    // Access the endpoint to get the swarm bounties
    try {


        const data = await getSwarmBounty();
        if (!data) {
            console.log("No data found");
            return;
        }
        const swarmBounties = data.data.filter((bounty: any) => bounty.swarmType === SwarmBountyType.DOCUMENT_SUMMARIZER);
        const docs = await DocumentationModel.find();
        console.log("swarmBounties", swarmBounties.length);
        // Create a map of existing specs by swarmBountyId for quick lookup
        const existingDocs = new Map(docs.map(doc => [doc.swarmBountyId, doc]));
        console.log("existingDocs", existingDocs.size);
        // Process each feature bounty
        for (const bounty of swarmBounties) {
            const bountyId = bounty._id.toString();
            if (!existingDocs.has(bountyId)) {
                // Create new spec if it doesn't exist
                await DocumentationModel.create({
                    repoOwner: bounty.githubUrl.split('/')[3], // Extract owner from GitHub URL
                    repoName: bounty.githubUrl.split('/')[4], // Extract repo name from GitHub URL
                    swarmBountyId: bountyId
                });
            }
        }
        } catch (error) {
        console.error("Error syncing DB", error);
    }
}
