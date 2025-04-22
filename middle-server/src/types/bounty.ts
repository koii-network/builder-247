export interface Bounty {
    _id: string;
    email: string;
    githubUrl: string;
    projectName: string;
    description: string;
    bountyAmount: number;
    isAutoIntegrationKit: boolean;
    swarmType: string;
    bountyType: string;
    walletAddress: string;
    txHash: string;
    status: string;
    network: string;
    createdAt: string;
    updatedAt: string;
    __v: number;
}

export interface BountyResponse {
    success: boolean;
    data: Bounty[];
} 