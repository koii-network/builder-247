import { SwarmBountyStatus } from "../../config/constant";
import { BountyResponse } from "../../types/bounty";

export async function getSwarmBounty(): Promise<BountyResponse | null> {
    const endpoint = `${process.env.PROMETHEUS_SERVER_URL}/api/v1/bounty?status=${SwarmBountyStatus.IN_PROGRESS}`;
    const response = await fetch(endpoint, {
        headers: {
            'Authorization': `Bearer ${process.env.PROMETHEUS_SERVER_X_API_KEY || ""}`
        }
    });
    
    if (!response.ok) {
        console.log("No data found");
        return null;
    }

    const data: BountyResponse = await response.json();
    return data;
}
