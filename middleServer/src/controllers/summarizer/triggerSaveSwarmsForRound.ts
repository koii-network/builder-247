import { Request, Response } from 'express';

import { getMaxSubmissionRound } from '../../taskOperations/getSubmissionRound';

import { getExistingIssues, getInitializedDocumentSummarizeIssues } from '../../swarmBountyOperations/existingIssues';

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

    // Check if this is the correct time to get the rounds
    const maxSubmissionRound = await getMaxSubmissionRound(taskId);
    if (!maxSubmissionRound) {
        res.status(401).send('No max submission round found');
        return;
    }
    if ( round > maxSubmissionRound + 1) {
        res.status(401).send('Not the correct time to get the rounds');
        return;
    }

    const existingIssues = await getExistingIssues();
    const initializedDocumentSummarizeIssues = await getInitializedDocumentSummarizeIssues(existingIssues);
    
    await saveSwarmsForRound(initializedDocumentSummarizeIssues);
}

export async function saveSwarmsForRound(issues:any[]) {
   
}