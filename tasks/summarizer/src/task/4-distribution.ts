import { Submitter, DistributionList } from "@_koii/task-manager";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import { customReward, status } from "../utils/constant";
import { Submission } from "@_koii/namespace-wrapper/dist/types";
import { middleServerUrl } from "../utils/constant";
import { getOrcaClient } from "@_koii/task-manager/extensions";
import { submissionJSONSignatureDecode } from "../utils/submissionJSONSignatureDecode";
import { getRandomNodes } from "../utils/leader";
const getSubmissionList = async (roundNumber: number): Promise<Record<string, Submission>> => {
  const submissionInfo = await namespaceWrapper.getTaskSubmissionInfo(roundNumber);
  return submissionInfo?.submissions[roundNumber] || {};
}
export const getEmptyDistributionList = async (
  submitters: Submitter[],
): Promise<DistributionList> => {
  const distributionList: DistributionList = {};
  for (const submitter of submitters) {
    distributionList[submitter.publicKey] = 0;
  }
  return distributionList;
}
export const distribution = async (
  submitters: Submitter[],
  bounty: number,
  roundNumber: number,
): Promise<DistributionList> => {
  /**
   * Generate the reward list for a given round
   * This function should return an object with the public keys of the submitters as keys
   * and the reward amount as values
   */
  try {
    const taskResult = await namespaceWrapper.storeGet(`result-${roundNumber}`);
    if (taskResult && taskResult !== status.ISSUE_SUCCESSFULLY_SUMMARIZED) {
      return await getEmptyDistributionList(submitters);
    }
    const orcaClient = await getOrcaClient();
    if (!orcaClient) {
      console.log("NO ORCA CLIENT");
      return await getEmptyDistributionList(submitters);
    }
    console.log(`MAKE DISTRIBUTION LIST FOR ROUND ${roundNumber}`);
    const distributionList: DistributionList = {};

    // Slash the stake of submitters who submitted incorrect values
    // and make a list of submitters who submitted correct values

    const response = await fetch(`${middleServerUrl}/api/summarizer/trigger-update-swarms-status`, {
      method: "POST",
      body: JSON.stringify({
        taskId: TASK_ID,
        round: roundNumber,
      }),
    });
    const data = await response.json();
    
    // Count transaction hashes
    const transactionHashCount = data.transactionHashs ? data.transactionHashs.length : 0;
    const randomNodes = await getRandomNodes(roundNumber, transactionHashCount);
    for (const submitter of submitters) {
      // TODO: Check if this guy is the one that should make submission
      // TODO: If not, then skip

      const submitterIndex = randomNodes.indexOf(submitter.publicKey);
      if (submitterIndex === -1) {
        distributionList[submitter.publicKey] = 0;
        continue;
      }
      // TODO: Check if this guy is making the submission that is supposed to be made(based on the index)
      const submitterSubmissions = await getSubmissionList(roundNumber);
      // get the submitter's submission
      const submitterSubmission = submitterSubmissions[submitter.publicKey];
      if (!submitterSubmission || submitterSubmission.submission_value === "") {
        distributionList[submitter.publicKey] = 0;
        continue;
      }
      const decodeResult = await submissionJSONSignatureDecode({submitterSubmission, submitter, roundNumber});
      console.log("decodeResult", decodeResult);
      if (!decodeResult) {
        console.error("INVALID SIGNATURE DATA");
        distributionList[submitter.publicKey] = 0;
        continue;
      }
      console.log("Sending audit request for submitter:", submitter.publicKey);
      console.log("Submission data being sent to audit:", decodeResult);
      
      const result = await orcaClient.podCall(`audit/${roundNumber}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          submission: decodeResult,
        }),
      });

      console.log("Raw audit result:", result);
      console.log("Audit result data type:", typeof result.data);
      console.log("Audit result data value:", result.data);
      
      if (result.data === true) {
        console.log(`✅ Audit passed for ${submitter.publicKey}`);
        console.log(`Setting reward to customReward value:`, customReward);
        distributionList[submitter.publicKey] = customReward;
      } else {
        console.log(`❌ Audit failed for ${submitter.publicKey}`);
        console.log("Failed audit result data:", result.data);
        distributionList[submitter.publicKey] = 0;
      }
      
      console.log("Current distribution list:", distributionList);
    }

    return distributionList;
  } catch (error) {
    console.error("ERROR IN DISTRIBUTION", error);
    return {};
  }
};
