import { Request, Response } from 'express';

import { getInitializedDocumentSummarizeIssues } from '../../swarmBountyOperations/existingIssues';
import { Octokit } from '@octokit/rest';
// A simple in-memory cache to store processed task IDs and rounds
const cache: Record<string, Set<number>> = {};

export async function triggerUpdateIssueStatus(req: Request, res: Response): Promise<void> {
    const { taskId, round } = req.body;

    // Check if the taskId and round have already been processed
    if (cache[taskId] && cache[taskId].has(round)) {
        res.status(200).send('Task already processed.');
        return;
    }

    // If not processed, add to cache
    if (!cache[taskId]) {
        cache[taskId] = new Set();
    }
    cache[taskId].add(round);

    const issues = await getInitializedDocumentSummarizeIssues(taskId);
    for (const issue of issues) {
        const repoStatus = await fetchGitRepoStatus(issue.githubUrl);
        console.log(repoStatus);
    }

    



}

export const fetchGitRepoStatus = async (githubUrl: string) => {
    const octokit = new Octokit({
        auth: process.env.GITHUB_TOKEN
    });
    
    const [owner, repo] = githubUrl.split('/').slice(3, 5);
    
    // Get all PRs that contain README in title
    const prs = await octokit.rest.pulls.list({
        owner,
        repo,
        per_page: 100
    });
    
    const prsWithReadme = prs.data.filter((pr: any) => pr.title.toLowerCase().includes('readme'));
    
    // Track PRs with approval comments
    const approvedPrs = [];
    
    // Check each PR for approval comments
    for (const pr of prsWithReadme) {
        const prComments = await octokit.rest.issues.listComments({
            owner,
            repo,
            issue_number: pr.number
        });
        
        const hasApproval = prComments.data.some(comment => 
            comment.body?.toLowerCase().includes('approve')
        );
             
        if (hasApproval) {
            return  true;
            // approvedPrs.push({
            //     prNumber: pr.number,
            //     title: pr.title,
            //     url: pr.html_url
            // });
        }
    }
    return false;

}

export const main = async () => {
    const hasApprovedReadmePr = await fetchGitRepoStatus("https://github.com/alexander-morris/koii-dumper-reveal");
    console.log(hasApprovedReadmePr);
}

main();