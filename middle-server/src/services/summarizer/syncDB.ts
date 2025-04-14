import { DocumentationModel } from "../../models/Documentation";
import { SwarmBountyStatus, SwarmBountyType } from "../../config/constant";

import dotenv from "dotenv";
dotenv.config();
// import SwarmBounty from "../../models/SwarmBounties";
export async function syncDB() {
  // Get all feature bounties
  // Access the endpoint to get the swarm bounties
  try {
    const endpoint = `${process.env.PROMETHEUS_SERVER_URL}/api/v1/bounty?status=${SwarmBountyStatus.IN_PROGRESS}`;
    const response = await fetch(endpoint, {
      headers: {
        Authorization: `Bearer ${process.env.PROMETHEUS_SERVER_X_API_KEY || ""}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error: ${response.status} ${response.statusText}`);
      console.error("Response body:", errorText);
      throw new Error(`API request failed with status ${response.status}`);
    }

    const data = await response.json();
    const swarmBounties = data.data.filter((bounty: any) => bounty.swarmType === SwarmBountyType.DOCUMENT_SUMMARIZER);
    const docs = await DocumentationModel.find();
    console.log("swarmBounties", swarmBounties.length);
    // Create a map of existing specs by swarmBountyId for quick lookup
    const existingDocs = new Map(docs.map((doc) => [doc.swarmBountyId, doc]));
    console.log("existingDocs", existingDocs.size);
    // Process each feature bounty
    for (const bounty of swarmBounties) {
      const bountyId = bounty._id.toString();
      if (!existingDocs.has(bountyId)) {
        // Create new spec if it doesn't exist
        await DocumentationModel.create({
          repoOwner: bounty.githubUrl.split("/")[3], // Extract owner from GitHub URL
          repoName: bounty.githubUrl.split("/")[4], // Extract repo name from GitHub URL
          swarmBountyId: bountyId,
        });
      }
    }
  } catch (error) {
    console.error("Error syncing DB", error);
  }
}
