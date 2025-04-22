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
  try {
    const distributionList: DistributionList = {};

    for (const submitter of submitters) {
      console.log(`\n[DISTRIBUTION] Processing submitter: ${submitter.publicKey}`);
      
      console.log(`[DISTRIBUTION] Getting submission list for round ${roundNumber}`);
      const submitterSubmissions = await getSubmissionList(roundNumber);
      console.log(`[DISTRIBUTION] Total submissions found: ${Object.keys(submitterSubmissions).length}`);
      
      const submitterSubmission = submitterSubmissions[submitter.publicKey];
      if (!submitterSubmission || submitterSubmission.submission_value === "") {
        console.log(`[DISTRIBUTION] ❌ No valid submission found for submitter ${submitter.publicKey}`);
        distributionList[submitter.publicKey] = 0;
        continue;
      }
      if (Object.values(status).includes(submitterSubmission.submission_value)) {
         distributionList[submitter.publicKey] = 0;
         continue;
      }else{
        // TODO: Check if I should include = 0 here 
        if (submitter.votes >= 0) {
          distributionList[submitter.publicKey] = customReward;
        }else{
          distributionList[submitter.publicKey] = 0;
        }
      }
    }

    console.log(`[DISTRIBUTION] ✅ Distribution completed successfully`);
    console.log(`[DISTRIBUTION] Final distribution list:`, distributionList);
    return distributionList;
  } catch (error: any) {
    console.error(`[DISTRIBUTION] ❌ ERROR IN DISTRIBUTION:`, error);
    console.error(`[DISTRIBUTION] Error stack:`, error.stack);
    return {};
  }
};
