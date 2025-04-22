import { AccountInfo, PublicKey, Connection } from "@_koii/web3.js";
import { decodeZstd } from "./decodeZstd";
import { getTaskStateInfo } from "@_koii/create-task-cli";
import { bincode_js_deserialize } from "../../utils/webasm_bincode_deserializer/bincode_js.js";

export async function getDistributionListSubmitter(taskId: string, round: string): Promise<string | null> {
  const connection = new Connection("https://mainnet.koii.network", "confirmed");

  try {
    const taskStateInfo = await getTaskStateInfo(connection, taskId);
    if (!taskStateInfo || !taskStateInfo.distribution_rewards_submission) {
      console.error("No distribution rewards submission found for task:", taskId);
      return null;
    }
    if (!taskStateInfo.distribution_rewards_submission[round]) {
      console.error("No distribution rewards submission found for round:", round);
      return null;
    }
    const keys = Object.keys(taskStateInfo.distribution_rewards_submission[round]);
    return keys.length > 0 ? keys[0] : null;
  } catch (error) {
    console.error("Error in getDistributionListSubmitter", error);
    return null;
  }
}

async function getDistributionList(publicKey: string, round: string, taskId: string): Promise<string | null> {
  const connection = new Connection("https://mainnet.koii.network", "confirmed");
  let accountInfo: AccountInfo<Buffer> | null = null;
  accountInfo = await connection.getAccountInfo(new PublicKey(publicKey), "base64+zstd");
  if (!accountInfo) {
    console.log(`${publicKey} doesn't contain any distribution list data`);
    return null;
  }
  accountInfo.data = await decodeZstd((accountInfo.data ? accountInfo.data[0] : "") + "");
  const origData = getBincodeDeserializedDistributionList(accountInfo?.data, round, taskId);
  if (origData) return origData;
  try {
    const d = JSON.parse(accountInfo.data + "");
    const i = Buffer.from(d[round][taskId]).indexOf(0x00);
    const t = Buffer.from(d[round][taskId]).slice(0, i);

    const origData = JSON.stringify(new TextDecoder().decode(t));
    return origData;
  } catch (error) {
    console.log("ERROR", error);
    return null;
  }
}

export function getBincodeDeserializedDistributionList(raw_data: any, round: string, taskId: string): string | null {
  try {
    if (!raw_data) return null;
    const jsObject = {};
    const parse_result = bincode_js_deserialize(raw_data);
    console.log("parse_result", parse_result);
    // @ts-ignore
    parse_result.forEach((innerMap: any, epoch: any) => {
      const innerJsObject = {};
      innerMap.forEach((value: any, key: any) => {
        // @ts-ignore
        innerJsObject[key] = JSON.parse(value);
      });
      // @ts-ignore
      jsObject[epoch] = innerJsObject;
    });
    // @ts-ignore
    return JSON.stringify(jsObject[round][taskId]);
  } catch (e) {
    console.error("Error in BincodeDeserialization", e);
    return null;
  }
}

export async function getDistributionListWrapper(taskId: string, round: string): Promise<object | null> {
  const submitter = await getDistributionListSubmitter(taskId, round);
  if (!submitter) {
    console.log("No submitter found");
    return null;
  }
  console.log("submitter", submitter);
  console.log("round", round);
  console.log("taskId", taskId);
  const distributionList = await getDistributionList(submitter, round, taskId);
  // console.log("distributionList", distributionList);
  if (distributionList) {
    try {
      // Check if distributionList is already an object
      // if (typeof distributionList === 'object') {
      //     return distributionList;
      // }
      // If it's a string, try to parse it
      const parsedList = JSON.parse(distributionList);
      return parsedList;
    } catch (error) {
      console.error("Error parsing distribution list:", error);
      return null;
    }
  }
  return null;
}

export async function getKeysByValueSign(
  distributionList: object,
): Promise<{ positive: string[]; negative: string[] }> {
  const positive: string[] = [];
  const negative: string[] = [];

  Object.entries(distributionList).forEach(([key, value]) => {
    const numValue = Number(value);
    if (numValue > 0) {
      positive.push(key);
    } else if (numValue <= 0) {
      negative.push(key);
    }
  });

  return { positive, negative };
}
//   async function main(){
//     const distributionList = await getDistributionListWrapper("FttDHvbX3nM13TUrSvvS614Sgtr9418TC8NpvR7hkMcE", "361");
//     if (distributionList) {
//         const positiveKeys = await getPositiveKeys(distributionList);
//         console.log(positiveKeys);
//     }
//   }

//   main();
