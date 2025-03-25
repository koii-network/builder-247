import { Submitter, DistributionList } from "@_koii/task-manager";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import { customReward, status } from "../utils/constant";
import { Submission } from "@_koii/namespace-wrapper/dist/types";

import { getOrcaClient } from "@_koii/task-manager/extensions";
import { submissionJSONSignatureDecode } from "../utils/submissionJSONSignatureDecode";
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
    for (const submitter of submitters) {
      const submitterSubmissions = await getSubmissionList(roundNumber);
      // get the submitter's submission
      const submitterSubmission = submitterSubmissions[submitter.publicKey];
      if (!submitterSubmission || submitterSubmission.submission_value === "") {
        distributionList[submitter.publicKey] = 0;
        continue;
      }
      const decodeResult = await submissionJSONSignatureDecode({submitterSubmission, submitter, roundNumber});
      if (!decodeResult) {
        console.error("INVALID SIGNATURE DATA");
        distributionList[submitter.publicKey] = 0;
        continue;
      }
  
  
      // Send the submission to the ORCA container for auditing
      const result = await orcaClient.podCall(`audit/${roundNumber}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          submission: decodeResult,
        }),
      });
      if (result.data === "true") {
        distributionList[submitter.publicKey] = customReward;
      } else {
        distributionList[submitter.publicKey] = 0;
      }

    }

    return distributionList;
  } catch (error) {
    console.error("ERROR IN DISTRIBUTION", error);
    return {};
  }
};
