import { Request, Response } from 'express';
import { getDistributionListSubmitter, getDistributionListWrapper, getKeysByValueSign } from '../../utils/taskState/getDistributionList';
import { SpecModel, SpecStatus } from "../../models/Spec";
import { plannerTaskID } from '../../config/constant';
import { SwarmBountyStatus } from '../../config/constant';
import { updateSwarmBountyStatus } from '../../services/swarmBounty/updateStatus';
import { TodoModel } from '../../models/Todo';
import { IssueModel } from '../../models/Issue';
import { getFile } from '../../utils/ipfs/ipfs';
import { initializeConnections } from '../../services/database/database';
import { IssueStatus } from '../../models/Issue';
// A simple in-memory cache to store processed task IDs and rounds
const cache: Record<string, Set<number>> = {};

interface Issue {
    uuid: string;
    title: string;
    description: string;
}

interface Task {
    acceptanceCriteria: string;
    assignedTo: string[];
    dependencyTasks: string[];
    description: string;
    issueUuid: string;
    repoName: string;
    repoOwner: string;
    status: string;
    title: string;
    uuid: string;
}

export async function triggerFetchAuditResult(req: Request, res: Response): Promise<void> {
    const { taskId, round } = req.body;
    console.log("[TRIGGER FETCH AUDIT RESULT] taskId: ", taskId);
    console.log("[TRIGGER FETCH AUDIT RESULT] round: ", round);
    if (taskId !== plannerTaskID) {
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

    const response = await triggerFetchAuditResultLogic(positiveKeys, negativeKeys, round);
    res.status(response.statuscode).json(response.data);

}

export const triggerFetchAuditResultLogic = async (positiveKeys: string[], negativeKeys: string[], round: number) => {
        console.log("positiveKeys", positiveKeys);
        console.log("negativeKeys", negativeKeys);
        console.log("round", round);
        // ============== Update the subtask status ==============
        try {
            const specs = await SpecModel.find({ "assignedTo.stakingKey": { $in: [...positiveKeys, ...negativeKeys] } });
            
            for (const spec of specs) {
                try {
                    for (const assignee of spec.assignedTo) {
                        if (!assignee.taskId || !assignee.roundNumber || !assignee.stakingKey) {
                            console.log('Missing required fields for assignee:', assignee);
                            continue;
                        }
                        if (positiveKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                            if (!assignee.prUrl) {
                                return {statuscode: 400, data: {
                                    success: false,
                                    message: 'No PR URL found for assignee.',
                                }};
                            }

                            const result = await processAuditResult({cid: assignee.prUrl, swarmBountyId: spec.swarmBountyId, repoName: spec.repoName, repoOwner: spec.repoOwner});
                            if (result) {
                                assignee.auditResult = true;
                            } else {
                                assignee.auditResult = false;
                            }
                    
                            spec.status = SpecStatus.DONE;
                            if (spec.swarmBountyId) {
                                await updateSwarmBountyStatus(spec.swarmBountyId, SwarmBountyStatus.COMPLETED);
                            }
                        } else if (negativeKeys.includes(assignee.stakingKey) && assignee.roundNumber === round) {
                            assignee.auditResult = false;
                        }
                    }
                    // Save the spec with error handling
                    try {
                        await spec.save();
                    } catch (saveError) {
                        console.error('Error saving spec:', saveError);
                        // Continue with next spec instead of failing the entire process
                        continue;
                    }
                } catch (assigneeError) {
                    console.error('Error processing assignee:', assigneeError);
                    // Continue with next spec
                    continue;
                }
            }
            
            return {statuscode: 200, data: {
                success: true,
                message: 'Task processed successfully.',
            }};
        } catch (error) {
            console.error('Error in triggerFetchAuditResultLogic:', error);
            return {statuscode: 500, data: {
                success: false,
                message: 'Internal server error while processing audit results.',
            }};
        }
}


export const processAuditResult = async ({cid, swarmBountyId, repoName, repoOwner}: {cid: string, swarmBountyId: string, repoName: string, repoOwner: string}) => {
    let decodedFile = null;
    try {
        decodedFile = await decodeFile(cid);
        if (!decodedFile) {
            return null;
        }
    } catch (error) {
        console.error("Error decoding file:", error);
        return null;
    }
    console.log("decodedFile", decodedFile);
    try {
        const { issues, tasks } = decodedFile;
        


        // Prepare bulk operations for tasks

        const taskOperations = tasks.map((task: Task) => (
            console.log({
                swarmBountyId: swarmBountyId,
                acceptanceCriteria: task.acceptanceCriteria,
                assignedTo: task.assignedTo,
                dependencyTasks: task.dependencyTasks,
                description: task.description,
                issueUuid: task.issueUuid,
                repoName: task.repoName,
                repoOwner: task.repoOwner,
                status: task.status,
                title: task.title,
                uuid: task.uuid,
            }),
            {
            insertOne: {
                document: {
                    swarmBountyId: swarmBountyId,
                    acceptanceCriteria: task.acceptanceCriteria,
                    assignedTo: task.assignedTo,
                    dependencyTasks: task.dependencyTasks,
                    description: task.description,
                    issueUuid: task.issueUuid,
                    repoName: task.repoName,
                    repoOwner: task.repoOwner,
                    status: task.status,
                    title: task.title,
                    uuid: task.uuid,
                }
            }
        }));
        // // Prepare bulk operations for issues
        const issueOperations = issues.map((issue: Issue) => ({
            insertOne: {
                document: {
                    swarmBountyId: swarmBountyId,
                    issueUuid: issue.uuid,
                    title: issue.title,
                    description: issue.description,
                    repoName: repoName,
                    repoOwner: repoOwner,
                    status: IssueStatus.INITIALIZED,
                    assignedTo: []
                }
            }
        }));
        // Execute bulk operations
   
        if (taskOperations.length > 0) {
            await TodoModel.bulkWrite(taskOperations);
        }
        if (issueOperations.length > 0) {
            await IssueModel.bulkWrite(issueOperations);
        }
        return true;
    } catch (error) {
        console.error("Error processing audit result:", error);
        return null;
    }
}
export const decodeFile = async (cid: string) => {
    try {
        const file = await getFile(cid);
        const decodedFile = JSON.parse(file);
        if (decodedFile.tasks && decodedFile.issues) {
            // Flatten the nested tasks array if it exists
            const flattenedTasks = Array.isArray(decodedFile.tasks[0]) ? decodedFile.tasks[0] : decodedFile.tasks;
            return {
                issues: decodedFile.issues,
                tasks: flattenedTasks,
            };
        }
    } catch (error) {
        console.error("Error decoding file:", error);
        return null;
    }
}



export const test = async () => {
    await initializeConnections();
    await triggerFetchAuditResultLogic(["0x123"], ["0x456"], 2);
}
test();