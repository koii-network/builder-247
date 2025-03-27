import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';

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

export async function generateHermanL02Bounties(): Promise<string> {
    const { Octokit } = await import('@octokit/rest');
    const octokit = new Octokit({
        auth: process.env.GITHUB_TOKEN
    });

    try {
        // Get all repositories for HermanL02
        const { data: repos } = await octokit.repos.listForUser({
            username: 'koii-network',
            per_page: 100
        });

        // Generate markdown header
        let markdown = `# Prometheus Swarm Bounties\n\n`;
        markdown += `| GitHub URL | Bounty Task | Project Name | Description | Bounty Amount | Bounty Type | Transaction Hash | Status |\n`;
        markdown += `|------------|------------|--------------|-------------|---------------|-------------|------------------|-------|\n`;

        // Generate markdown rows
        repos.forEach((repo: Repository) => {
            const transactionHash = uuidv4().replace(/-/g, '');
            const bountyAmount = Math.floor(Math.random() * 50) + 1;
            
            markdown += `|[${repo.name}](${repo.html_url})|Document & Summarize|${repo.name}|Document and summarize the ${repo.name} repository|${bountyAmount}|usdc|${transactionHash}|Initialized|\n`;
        });

        return markdown;
    } catch (error) {
        console.error('Error generating bounties:', error);
        throw error;
    }
}

// Example usage:
async function main() { 
    const markdown = await generateHermanL02Bounties();
    console.log(markdown);
}

main();
