import { SpecModel } from "../../models/Spec";
// import SwarmBounty from "../../models/SwarmBounties";
import { SwarmBountyType, SwarmBountyStatus } from "../../config/constant";
import { createFork } from "../../utils/gitHub/gitHub";
export async function syncDB() {
    // Get all feature bounties
    const endpoint = `${process.env.PROMETHEUS_SERVER_URL}?status=${SwarmBountyStatus.IN_PROGRESS}`;
    const response = await fetch(endpoint, {
        headers: {
            'Authorization': `Bearer ${process.env.PROMETHEUS_SERVER_X_API_KEY || ""}`
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        console.error(`API Error: ${response.status} ${response.statusText}`);
        console.error('Response body:', errorText);
        throw new Error(`API request failed with status ${response.status}`);
    }

    const data = await response.json();
    const swarmBounties = data.data.filter((bounty: any) => bounty.swarmType === SwarmBountyType.BUILD_FEATURE);
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
