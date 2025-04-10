import { SwarmBountyStatus } from "../../config/constant";
import dotenv from "dotenv";
dotenv.config();
export async function updateSwarmBountyStatus(swarmBountyId: string, status: SwarmBountyStatus){
    try {
        const endpoint = `${process.env.PROMETHEUS_SERVER_URL}/api/v1/bounty`;

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.PROMETHEUS_SERVER_X_API_KEY || ""}`
            },
            body: JSON.stringify({ id: swarmBountyId, status: status }),
 
        });
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API Error: ${response.status} ${response.statusText}`);
            console.error('Response body:', errorText);
            throw new Error(`API request failed with status ${response.status}`);
        }
        return response.json();
    } catch (error) {
        console.error("Error updating swarm bounty status", error);
    }

}

export async function test(){
    const swarmBountyId = "67d9aab4c9b0094618ef449c";
    const status = SwarmBountyStatus.ASSIGNED;
    const response = await updateSwarmBountyStatus(swarmBountyId, status);
    console.log(response);
}


test();