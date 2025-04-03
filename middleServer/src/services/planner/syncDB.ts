import { SpecModel } from "../../models/Spec";
import SwarmBounty from "../../models/SwarmBounties";
import { createFork } from "../../utils/gitHub/gitHub";
export async function syncDB() {
    // Get all feature bounties
    const swarmBounties = await SwarmBounty.find({ swarmType: "feature" });
    const specs = await SpecModel.find();

    // Create a map of existing specs by swarmBountyId for quick lookup
    const existingSpecs = new Map(specs.map(spec => [spec.swarmBountyId, spec]));

    // Process each feature bounty
    for (const bounty of swarmBounties) {
        const bountyId = bounty._id.toString();
        if (!existingSpecs.has(bountyId)) {
            // Create new spec if it doesn't exist
            await SpecModel.create({
                title: bounty.projectName,
                description: bounty.description,
                repoOwner: bounty.githubUrl.split('/')[3], // Extract owner from GitHub URL
                repoName: bounty.githubUrl.split('/')[4], // Extract repo name from GitHub URL
                swarmBountyId: bountyId
            });
            // Create a fork for this bounty
            await createFork(bounty.githubUrl);
        }
    }
}
