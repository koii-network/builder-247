import { getTaskStateInfo } from "@_koii/create-task-cli";
import { Connection } from "@_koii/web3.js";
import { RPCURL, taskID } from "../constant";
import NodeCache from "node-cache";

const taskCache = new NodeCache({ stdTTL: 30, checkperiod: 120 });

export async function getTaskState(taskId: string): Promise<String[]> {
  const cachedTaskState = taskCache.get(taskId);
  if (cachedTaskState) {
    return cachedTaskState as String[];
  }

  const connection = new Connection(RPCURL);
  const taskState = await getTaskStateInfo(connection, taskId);
  //   console.log(Object.keys(taskState.stake_list));
  const stakeListKeys = Object.keys(taskState.stake_list);

  taskCache.set(taskId, stakeListKeys);
  return stakeListKeys;
}

export async function isValidStakingKey(pubKey: string): Promise<boolean> {
  const stakeListKeys = await getTaskState(taskID);
  return stakeListKeys.includes(pubKey);
}
// async function test() {
//   const stakeListKeys = await getTaskState("H5CKDzSi2qWs7y7JGMX8sGvAZnWcUDx8k1mCMVWyJf1M");
//   console.log(stakeListKeys);
//   console.log(1)
//     const stakeList = await getTaskState("H5CKDzSi2qWs7y7JGMX8sGvAZnWcUDx8k1mCMVWyJf1M");
//     console.log(stakeList);
//     console.log(2)
// }
// test();
