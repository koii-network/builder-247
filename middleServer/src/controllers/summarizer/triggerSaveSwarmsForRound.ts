import { Request, Response } from 'express';

import { getCurrentRound } from '../../utils/taskState/getSubmissionRound';
import { SwarmBountyType } from '../../models/SwarmBounties';
import { getInitializedIssuesMongoDB } from '../../services/swarmBounty/existingIssues';
import { SummarizerRecordModel } from '../../models/Summarizer';
import { updateStatus } from '../../services/swarmBounty/updateStatus';
import { SwarmBountyStatus } from '../../models/SwarmBounties';
import dotenv from 'dotenv';

dotenv.config();
// A simple in-memory cache to store processed task IDs and rounds
const cache: Record<string, Record<number, { data: any, promise?: Promise<any> }>> = {};

export async function triggerSaveSwarmsForRound(req: Request, res: Response): Promise<void> {
    const { taskId, round } = req.body;
    // Check if both taskId and round are provided
    if (process.env.TASK_ID_SUMMARIZER) {
        if (taskId !== process.env.TASK_ID_SUMMARIZER) {
            res.status(400).send('Task ID is not correct');
            return;
        }
    }
    if (!taskId || !round) {
        res.status(400).send('Task ID and round are required');
        return;
    }
    // Initialize task cache if it doesn't exist
    if (!cache[taskId]) {
        cache[taskId] = {};
    }

    // Check if there's cached data for this taskId and round
    if (cache[taskId][round]) {
        if (cache[taskId][round].data) {
            // If we have resolved data, return it immediately
            res.status(200).send(cache[taskId][round].data);
            return;
        } else if (cache[taskId][round].promise) {
            // If we have an ongoing promise, wait for it
            try {
                const result = await cache[taskId][round].promise;
                cache[taskId][round].data = result;
                delete cache[taskId][round].promise;
                res.status(200).send(result);
            } catch (error) {
                console.error(error);
                res.status(500).send('Error processing request');
            }
            return;
        }
    }

    // Create a new promise for this request
    const processPromise = (async () => {
        // Check if this round already exists

        // Check if this is the correct time to get the rounds
        const currentRound = await getCurrentRound(taskId);
        if (Number(round) !== currentRound){
            res.status(400).send('Not the correct time to get the rounds');
            return;
        }
        
        const existingSwarms = await SummarizerRecordModel.findOne({ taskID: taskId, roundNumber: round });
        if (existingSwarms) {
            return existingSwarms;
        }
        const initializedDocumentSummarizeIssues = await getInitializedIssuesMongoDB(SwarmBountyType.DOCUMENT_SUMMARIZER);
        const issuesToSave = [];
        for (const issue of initializedDocumentSummarizeIssues) {
            const isRequiredToAssignAgainResult = await isRequiredToAssignAgain(issue.githubUrl);
            if (isRequiredToAssignAgainResult) {
                issuesToSave.push(issue);
            }
        }
        return await saveSwarmsForRound(taskId, round, issuesToSave);
    })();

    // Store the promise in cache
    cache[taskId][round] = {
        promise: processPromise,
        data: null
    };

    try {
        const result = await processPromise;
        cache[taskId][round].data = result;
        delete cache[taskId][round].promise;
        res.status(200).send(result);
    } catch (error) {
        console.error(error);
        res.status(500).send('Error processing request');
    }
}

export async function saveSwarmsForRound(taskID:string, roundNumber:number, issues:any[]) {
   const issueTransactionHashs = issues.map((issue) => issue.txHash);
   const summarizerRecord = new SummarizerRecordModel({
    taskID: taskID,
    roundNumber: roundNumber,
    transactionHashs: issueTransactionHashs,
   });
   await summarizerRecord.save();
   return summarizerRecord;
}

export const isRequiredToAssignAgain = async (githubUrl: string) => {
    const { Octokit } = await import('@octokit/rest');
    const octokit = new Octokit({
        auth: process.env.GITHUB_TOKEN
    });
    
    const [owner, repo] = githubUrl.split('/').slice(3, 5);
    
    // Check if repository is archived and has Git content
    try {
        const repoInfo = await octokit.rest.repos.get({
            owner,
            repo
        });
        
        if (repoInfo.data.archived) {
            console.log(`${githubUrl} is archived, skipping`);
            await updateStatus(githubUrl, SwarmBountyStatus.FAILED);
            return false;
        }

        // Check if repository is private
        if (repoInfo.data.private) {
            console.log(`${githubUrl} is private, skipping`);
            await updateStatus(githubUrl, SwarmBountyStatus.FAILED);
            return false;
        }

        // Check if repository is a fork
        if (repoInfo.data.fork) {
            console.log(`${githubUrl} is a fork, skipping`);
            await updateStatus(githubUrl, SwarmBountyStatus.FAILED);
            return false;
        }

        // Check if repository has any commits
        const commits = await octokit.rest.repos.listCommits({
            owner,
            repo,
            per_page: 1
        });

        if (commits.data.length === 0) {
            console.log(`${githubUrl} has no Git content, skipping`);
            await updateStatus(githubUrl, SwarmBountyStatus.FAILED);
            return false;
        }
    } catch (error: any) {
        if (error.status === 403 && error.message?.includes('contains no Git content')) {
            console.log(`${githubUrl} has no Git content, skipping`);
        } else {
            console.error(`Error checking repository status for ${githubUrl}:`, error);
        }
        await updateStatus(githubUrl, SwarmBountyStatus.FAILED);
        return false;
    }
    
    // Get all PRs that contain README in title
    const prs = await octokit.rest.pulls.list({
        owner,
        repo,
        per_page: 100
    });
    // If not assigned
    if (prs.data.length === 0) {
        return true;
    }
    const prsWithReadme = prs.data.filter((pr: any) => pr.title.toLowerCase().includes('prometheus: add readme for'));
    if (prsWithReadme.length === 0) {
        return true;
    }
    // Track PRs with approval comments
    const revisedPrs = [];
    const noCommentsPrs = [];
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
            console.log(`${githubUrl} has been approved`);
            await updateStatus(githubUrl, SwarmBountyStatus.COMPLETED);
            return false
        }

        const hasRevised = prComments.data.some(comment => 
            comment.body?.toLowerCase().includes('revise')
        );

        if (hasRevised) {
            revisedPrs.push(pr);
        } else {
            // if this pr is within 3 hours
            const prCreatedAt = new Date(pr.created_at);
            const threeHoursAgo = new Date(Date.now() - 3 * 60 * 60 * 1000);
            if (prCreatedAt > threeHoursAgo) {
                noCommentsPrs.push(pr);
            }
        }
    }
    if (noCommentsPrs.length > 0) {
        return false;
    }
    // or assigned and need to be revised
    if (revisedPrs.length > 0) {
        return true;
    }
    return true;
}