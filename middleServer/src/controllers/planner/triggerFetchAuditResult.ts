import { Request, Response } from 'express';
import { KoiiStorageClient } from '@_koii/storage-task-sdk';
import { getDistributionListSubmitter, getDistributionListWrapper, getKeysByValueSign } from '../../utils/taskState/getDistributionList';
import { SpecModel, SpecStatus } from "../../models/Spec";
import { IssueModel } from '../../models/Issue';
import { getFile } from '../../utils/ipfs/ipfs';
import { TodoModel } from '../../models/Todo';
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
        const specs = await SpecModel.find({ "assignedTo.stakingKey": { $in: [...positiveKeys, ...negativeKeys] } });
        // console.log('Todos Found');
        for (const spec of specs) {
            for (const assignee of spec.assignedTo) {
                if (positiveKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                    if (assignee.ipfsCid) {
                        await addToIssuesAndTodos(assignee.ipfsCid);
                    }else{
                        return {statuscode: 500, data: {
                            success: false,
                            message: 'No IPFS CID found for the assignee',
                        }};
                    }
                    assignee.auditResult = true;
                    spec.status = SpecStatus.DONE;
                } else if (negativeKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                    assignee.auditResult = false;
                }
            }
            // Save the todo
            await spec.save();
        }
        
    return {statuscode: 200, data: {
        success: true,
        message: 'Task processed successfully.',
    }};
}
export const addToIssuesAndTodos = async (ipfsCid: string) =>{
    const data = await getFile(ipfsCid);
    const issues = JSON.parse(data).issues;
    const todos = JSON.parse(data).todos;
    for (const issue of issues) {
        const issueModel = new IssueModel(issue);
        await issueModel.save();
    }
    for (const todo of todos) {
        const todoModel = new TodoModel(todo);
        await todoModel.save();
    }
}
