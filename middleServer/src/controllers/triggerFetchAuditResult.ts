import { Request, Response } from 'express';
import { IssueModel } from '../models/Issue';
import { getDistributionListSubmitter, getDistributionListWrapper, getKeysByValueSign } from '../utils/taskState/getDistributionList';
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

    const distributionList = await getDistributionListWrapper(taskId, round);
    
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

    const response = await triggerFetchAuditResultLogic(positiveKeys, negativeKeys, round);
    res.status(response.statuscode).json(response.data);

}

export const triggerFetchAuditResultLogic = async (positiveKeys: string[], negativeKeys: string[], round: number) => {

        // ============== Update the subtask status ==============
        const todos = await TodoModel.find({ "assignedTo.stakingKey": { $in: [...positiveKeys, ...negativeKeys] } });
        // console.log('Todos Found');
        for (const todo of todos) {
            for (const assignee of todo.assignedTo) {
                if (positiveKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                    assignee.auditResult = true;
                    todo.status = TodoStatus.AUDITED;
                } else if (negativeKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                    assignee.auditResult = false;
                }
            }
            // Save the todo
            await todo.save();
        }
        // console.log('Todo Saved');
        // get all the issue's for this round changed todos
        const issueUuids = todos.map((todo) => todo.issueUuid);
        // Check if all subtasks of an issue are completed, if so, update the issue status to assign pending
        const issues = await IssueModel.find({ issueUuid: { $in: issueUuids } });
        for (const issue of issues) {
            const todos = await TodoModel.find({ issueUuid: issue.issueUuid });
            if (todos.every((todo) => todo.status === TodoStatus.AUDITED)) {
                issue.status = IssueStatus.ASSIGN_PENDING;
            }
            // Save the issue
            await issue.save();
        }
        // console.log('Issue Saved');

        // Now update the has pr issues
        const hasPRIssues = await IssueModel.find({"assignedTo.stakingKey": {$in: [...positiveKeys, ...negativeKeys]}, "assignedTo.prUrl": {$exists: true}});
        for (const issue of hasPRIssues) {
            for (const assignee of issue.assignedTo) {
                if (positiveKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                    issue.status = IssueStatus.IN_REVIEW;
                    assignee.auditResult = true;
                } else if (negativeKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                    assignee.auditResult = false;
                }
            }
            if (issue.status === IssueStatus.IN_REVIEW) {
                await TodoModel.updateMany({issueUuid: issue.issueUuid}, {$set: {status: TodoStatus.MERGED}});
            }
            await issue.save();
        }
    return {statuscode: 200, data: {
        success: true,
        message: 'Task processed successfully.',
    }};
}