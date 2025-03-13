import { Request, Response } from 'express';
import { IssueModel } from '../models/Issue';
import { getDistributionListSubmitter, getDistributionListWrapper, getKeysByValueSign } from '../taskOperations/getDistributionList';
import { IssueStatus } from '../models/Issue';
import { TodoModel, TodoStatus } from "../models/Todo";
// A simple in-memory cache to store processed task IDs and rounds
const cache: Record<string, Set<number>> = {};

export async function triggerFetchAuditResult(req: Request, res: Response): Promise<void> {
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
    const submitter = await getDistributionListSubmitter(taskId, round);
    if (!submitter) {
        cache[taskId].delete(round);
        res.status(200).send('No Distribution List Submitter found.');
        return;
    }

    const distributionList = await getDistributionListWrapper("FttDHvbX3nM13TUrSvvS614Sgtr9418TC8NpvR7hkMcE", "361");
    
    let positiveKeys: string[] = [];
    let negativeKeys: string[] = [];
    if (distributionList) {
        const { positive, negative } = await getKeysByValueSign(distributionList);
        positiveKeys = positive;
        negativeKeys = negative;
        
    }else{
        cache[taskId].delete(round);
        res.status(200).send('No Distribution List found.');
        return;
    }
    // ============== Update the subtask status ==============
    const todos = await TodoModel.find({ "assignedTo.stakingKey": { $in: [...positiveKeys, ...negativeKeys] } });

    for (const todo of todos) {
        for (const assignee of todo.assignedTo) {
            if (positiveKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                assignee.auditResult = true;
                todo.status = TodoStatus.AUDITED;
            } else if (negativeKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                assignee.auditResult = false;
                todo.status = TodoStatus.INITIALIZED;
            }
        }
        // Save the todo
        await todo.save();
    }
    // Get all the todos issueUuid
    const issueUuids = todos.map((todo) => todo.issueUuid);
    // Check if all subtasks of an issue are completed, if so, update the issue status
    const issues = await IssueModel.find({ issueUuid: { $in: issueUuids } });
    for (const issue of issues) {
        const todos = await TodoModel.find({ issueUuid: issue.issueUuid });
        if (todos.every((todo) => todo.status === TodoStatus.AUDITED)) {
            issue.status = IssueStatus.ASSIGN_PENDING;
        }
        // Save the issue
        await issue.save();
    }
    res.status(200).send('Task processed successfully.');
}

