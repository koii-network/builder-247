import { getTaskStateInfo } from "@_koii/create-task-cli";
import { Connection } from "@_koii/web3.js";
import { RPCURL, BYPASS_TASK_STATE_CHECK } from "../../config/constant";
import NodeCache from "node-cache";
import "dotenv/config";

const taskCache = new NodeCache({ stdTTL: 30, checkperiod: 120 });

async function getTaskStateStakingKeys(taskId: string): Promise<string[]> {
  const cachedTaskState = taskCache.get(taskId);
  if (cachedTaskState) {
    return cachedTaskState as string[];
  }

  const connection = new Connection(RPCURL);
  const taskState = await getTaskStateInfo(connection, taskId);
  //   console.log(Object.keys(taskState.stake_list));
  const stakeListKeys = Object.keys(taskState.stake_list);

  taskCache.set(taskId, stakeListKeys);
  return stakeListKeys;
}

export async function isValidStakingKey(taskId: string, pubKey: string): Promise<boolean> {
  // Skip blockchain checks during testing
  if (BYPASS_TASK_STATE_CHECK) {
    console.log(`[TEST MODE] Bypassing task state check for stakingKey: ${pubKey}`);
    return true;
  }

  let stakeListKeys: string[];
  try {
    stakeListKeys = await getTaskStateStakingKeys(taskId);
  } catch (error) {
    console.log("Error fetching task state", error);
    return true;
  }
  return stakeListKeys.includes(pubKey);
}
