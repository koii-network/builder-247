import { Request, Response } from 'express';
import { getDistributionListSubmitter, getDistributionListWrapper, getKeysByValueSign } from '../../utils/taskState/getDistributionList';
import { StarFollowModel } from "../../models/StarFollow";
import { SUPPORTER_TASK_ID } from '../../config/constant';
import { SwarmBountyStatus } from '../../config/constant';
import { updateSwarmBountyStatus } from '../../services/swarmBounty/updateStatus';
// import SwarmBounty, { SwarmBountyStatus } from '../../models/SwarmBounties';
// A simple in-memory cache to store processed task IDs and rounds
const cache: Record<string, Set<number>> = {};

export async function triggerFetchAuditResult(req: Request, res: Response): Promise<void> {
    const { taskId, round } = req.body;
    console.log("[TRIGGER FETCH AUDIT RESULT] taskId: ", taskId);
    console.log("[TRIGGER FETCH AUDIT RESULT] round: ", round);
    if (taskId !== SUPPORTER_TASK_ID) {
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
    console.log("distributionList", distributionList);
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

    const response = await triggerFetchAuditResultLogic(positiveKeys, negativeKeys);
    res.status(response.statuscode).json(response.data);

}

export const triggerFetchAuditResultLogic = async (positiveKeys: string[], negativeKeys: string[]) => {
        // ============== Update the subtask status ==============
        const starFollows = await StarFollowModel.find({ stakingKey: { $in: [...positiveKeys, ...negativeKeys] } });
        // console.log('Todos Found');
        for (const starFollow of starFollows) {
            // complete repos append pending repos
            starFollow.completedRepos = [...starFollow.completedRepos, ...starFollow.pendingRepos];
            starFollow.pendingRepos = [];
            // Save the todo
            await starFollow.save();
        }
        
        return {statuscode: 200, data: {
            success: true,
            message: 'Task processed successfully.',
        }};
}

// async function test(){
//     const response = await triggerFetchAuditResultLogic(["G79TK8ccVx11JCsStBY85thohoSCm5eDwACAVju4z7bj"], ["0x456"], 13);
//     console.log(response);
// }

// test();