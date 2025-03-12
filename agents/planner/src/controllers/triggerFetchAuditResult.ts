import { Request, Response } from 'express';

// A simple in-memory cache to store processed task IDs and rounds
const cache: Record<string, Set<number>> = {};

export function triggerFetchAuditResult(req: Request, res: Response): void {
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

    // Dummy processing logic
    // ... existing code ...

    res.status(200).send('Task processed successfully.');
}
