import { SwarmBountyStatus } from "../../config/constant";

export async function updateSwarmBountyStatus(swarmBountyId: string, status: SwarmBountyStatus){
    const endpoint = `${process.env.PROMETHEUS_SERVER_URL}/api/v1/bounty/${swarmBountyId}`;
    const response = await fetch(endpoint, {
        method: 'POST',
        body: JSON.stringify({ id: swarmBountyId, status: status }),
        headers: {
            'Authorization': `Bearer ${process.env.PROMETHEUS_SERVER_X_API_KEY || ""}`
        }
    });
}