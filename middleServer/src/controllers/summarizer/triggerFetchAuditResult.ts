import { Request, Response } from 'express';
import { getDistributionListSubmitter, getDistributionListWrapper, getKeysByValueSign } from '../../utils/taskState/getDistributionList';
import { DocumentationModel, DocumentationStatus } from "../../models/Documentation";
import { documentSummarizerTaskID } from '../../config/constant';
import SwarmBounty, { SwarmBountyStatus } from '../../models/SwarmBounties';
// A simple in-memory cache to store processed task IDs and rounds
const cache: Record<string, Set<number>> = {};

export async function triggerFetchAuditResult(req: Request, res: Response): Promise<void> {
    const { taskId, round } = req.body;
    if (taskId !== documentSummarizerTaskID) {
        res.status(400).send('Invalid task ID.');
        return;
    }
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
export async function updateSwarmBountyStatus(swarmBountyId: string, status: SwarmBountyStatus){
    const swarmBounty = await SwarmBounty.findById(swarmBountyId);
    if (!swarmBounty) {
        return;
    }
    swarmBounty.status = status;
    await swarmBounty.save();
}
export const triggerFetchAuditResultLogic = async (positiveKeys: string[], negativeKeys: string[], round: number) => {

        // ============== Update the subtask status ==============
        const specs = await DocumentationModel.find({ "assignedTo.stakingKey": { $in: [...positiveKeys, ...negativeKeys] } });
        // console.log('Todos Found');
        for (const spec of specs) {
            for (const assignee of spec.assignedTo) {
                if (positiveKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                    assignee.auditResult = true;
                    spec.status = DocumentationStatus.DONE;
                    if (spec.swarmBountyId) {
                        await updateSwarmBountyStatus(spec.swarmBountyId, SwarmBountyStatus.COMPLETED);
                    }
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

// async function test(){
//     const response = await triggerFetchAuditResultLogic(["0x123"], ["0x456"], 1);
//     console.log(response);
// }

// test();