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
  console.log(`[DISTRIBUTION] Starting distribution for round ${roundNumber}`);
  console.log(`[DISTRIBUTION] Number of submitters: ${submitters.length}`);
  console.log(`[DISTRIBUTION] Bounty amount: ${bounty}`);
  
  try {
    console.log(`[DISTRIBUTION] Checking task result for round ${roundNumber}`);
    const taskResult = await namespaceWrapper.storeGet(`result-${roundNumber}`);
    console.log(`[DISTRIBUTION] Task result:`, taskResult);
    
    if (taskResult && taskResult !== status.ISSUE_SUCCESSFULLY_SUMMARIZED) {
      console.log(`[DISTRIBUTION] Task not successfully summarized, returning empty distribution list`);
      return await getEmptyDistributionList(submitters);
    }

    console.log(`[DISTRIBUTION] Getting Orca client`);
    const orcaClient = await getOrcaClient();
    if (!orcaClient) {
      console.log("[DISTRIBUTION] ❌ NO ORCA CLIENT AVAILABLE");
      return await getEmptyDistributionList(submitters);
    }
    console.log(`[DISTRIBUTION] ✅ Orca client obtained successfully`);

    console.log(`[DISTRIBUTION] Creating distribution list for round ${roundNumber}`);
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
      console.log(`[DISTRIBUTION] ✅ Found submission for submitter ${submitter.publicKey}`);

      console.log(`[DISTRIBUTION] Decoding submission signature`);
      const decodeResult = await submissionJSONSignatureDecode({submitterSubmission, submitter, roundNumber});
      console.log(`[DISTRIBUTION] Decode result:`, decodeResult);
      
      if (!decodeResult) {
        console.error(`[DISTRIBUTION] ❌ INVALID SIGNATURE DATA for submitter ${submitter.publicKey}`);
        distributionList[submitter.publicKey] = 0;
        continue;
      }
      console.log(`[DISTRIBUTION] ✅ Signature decoded successfully`);

      console.log(`[DISTRIBUTION] Checking summarizer status for submitter ${submitter.publicKey}`);
      const checkSummarizerResponse = await fetch(`${middleServerUrl}/api/summarizer/check-summarizer`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
          stakingKey: submitter.publicKey, 
          roundNumber, 
          githubUsername: decodeResult.githubUsername, 
          prUrl: decodeResult.prUrl 
        }),
      });
      const checkSummarizerJSON = await checkSummarizerResponse.json();
      console.log(`[DISTRIBUTION] Summarizer check response:`, checkSummarizerJSON);
      
      if (!checkSummarizerJSON.success) {
        console.log(`[DISTRIBUTION] ❌ Audit failed for ${submitter.publicKey}`);
        distributionList[submitter.publicKey] = 0;
        continue;
      }
      console.log(`[DISTRIBUTION] ✅ Summarizer check passed`);

      console.log(`[DISTRIBUTION] Sending audit request for submitter: ${submitter.publicKey}`);
      console.log(`[DISTRIBUTION] Submission data being sent to audit:`, decodeResult);
      
      const result = await orcaClient.podCall(`audit/${roundNumber}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          submission: decodeResult,
        }),
      });

      console.log(`[DISTRIBUTION] Raw audit result:`, result);
      console.log(`[DISTRIBUTION] Audit result data type:`, typeof result.data);
      console.log(`[DISTRIBUTION] Audit result data value:`, result.data);
      
      if (result.data === true) {
        console.log(`[DISTRIBUTION] ✅ Audit passed for ${submitter.publicKey}`);
        console.log(`[DISTRIBUTION] Setting reward to customReward value:`, customReward);
        distributionList[submitter.publicKey] = customReward;
      } else {
        console.log(`[DISTRIBUTION] ❌ Audit failed for ${submitter.publicKey}`);
        console.log(`[DISTRIBUTION] Failed audit result data:`, result.data);
        distributionList[submitter.publicKey] = 0;
      }
      
      console.log(`[DISTRIBUTION] Current distribution list:`, distributionList);
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
