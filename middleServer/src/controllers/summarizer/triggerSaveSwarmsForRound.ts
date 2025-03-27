import { Request, Response } from 'express';

import { getMaxSubmissionRound } from '../../taskOperations/getSubmissionRound';

import { getExistingIssues, getInitializedDocumentSummarizeIssues } from '../../swarmBountyOperations/existingIssues';
import { SummarizerRecordModel } from '../../models/Summarizer';

// A simple in-memory cache to store processed task IDs and rounds
const cache: Record<string, Record<number, { data: any, promise?: Promise<any> }>> = {};

export async function triggerSaveSwarmsForRound(req: Request, res: Response): Promise<void> {
    const { taskId, round } = req.body;

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
        const existingSwarms = await SummarizerRecordModel.findOne({ taskID: taskId, roundNumber: round });
        if (existingSwarms) {
            return existingSwarms;
        }
        // Check if this is the correct time to get the rounds
        const maxSubmissionRound = await getMaxSubmissionRound(taskId);
        if (!maxSubmissionRound) {
            throw new Error('No max submission round found');
        }
        if (round > maxSubmissionRound + 1) {
            throw new Error('Not the correct time to get the rounds');
        }

        const existingIssues = await getExistingIssues();
        const initializedDocumentSummarizeIssues = await getInitializedDocumentSummarizeIssues(existingIssues);
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
   const issueTransactionHashs = issues.map((issue) => issue.transactionHash);
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
    const prsWithReadme = prs.data.filter((pr: any) => pr.title.toLowerCase().includes('readme'));
    
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
            return  false
        }

        const hasRevised = prComments.data.some(comment => 
            comment.body?.toLowerCase().includes('revised')
        );

        if (hasRevised) {
            revisedPrs.push(pr);
        } else {
            noCommentsPrs.push(pr);
        }
    }
    if (noCommentsPrs.length > 0) {
        return false;
    }
    // or assigned and need to be revised
    if (revisedPrs.length > 0) {
        return true;
    }
    return false;
}