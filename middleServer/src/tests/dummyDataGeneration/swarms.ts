import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import mongoose from 'mongoose';
import SwarmBountyModel, { SwarmBountyStatus } from '../../models/SwarmBounties';
dotenv.config();

interface BountyData {
    githubUrl: string;
    bountyTask: string;
    projectName: string;
    description: string;
    bountyAmount: number;
    bountyType: string;
    transactionHash: string;
    status: string;
}

interface Repository {
    html_url: string;
    name: string;
}
async function connectToDatabase() {
    await mongoose.connect(process.env.MONGODB_URI!);
}
export async function generateHermanL02Bounties(): Promise<string> {
    const { Octokit } = await import('@octokit/rest');
    const octokit = new Octokit({
        auth: process.env.GITHUB_TOKEN
    });

    try {
        // Get all repositories for HermanL02
        const { data: repos } = await octokit.repos.listForUser({
            username: 'somali0128',
            per_page: 100
        });

        // Generate markdown header
        let markdown = `# Prometheus Swarm Bounties\n\n`;
        markdown += `| GitHub URL | Bounty Task | Project Name | Description | Bounty Amount | Bounty Type | Transaction Hash | Status |\n`;
        markdown += `|------------|------------|--------------|-------------|---------------|-------------|------------------|-------|\n`;

        // Generate markdown rows
        const markdownRows = await Promise.all(repos.map(async (repo: Repository) => {
            const transactionHash = uuidv4().replace(/-/g, '');
            const bountyAmount = Math.floor(Math.random() * 50) + 1;
            const bounty = new SwarmBountyModel({
                githubUrl: repo.html_url,
                swarmType: "document-summarizer",
                projectName: repo.name,
                description: `Document and summarize the ${repo.name} repository`,
                bountyAmount: bountyAmount,
                bountyType: "usdc",
                status: SwarmBountyStatus.LOADING,
                txHash: transactionHash,
                walletAddress: "0x0000000000000000000000000000000000000000",
            });
            await bounty.save();
            return `|[${repo.name}](${repo.html_url})|Document & Summarize|${repo.name}|Document and summarize the ${repo.name} repository|${bountyAmount}|usdc|${transactionHash}|In Progress|\n`;
        }));

        markdown += markdownRows.join('');
        return markdown;
    } catch (error) {
        console.error('Error generating bounties:', error);
        throw error;
    }
}

// Example usage:
async function main() { 
    await connectToDatabase();
    const markdown = await generateHermanL02Bounties();
    console.log(markdown);
}

main();
