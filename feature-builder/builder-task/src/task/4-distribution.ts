import { Submitter, DistributionList } from "@_koii/task-manager";
import { namespaceWrapper } from "@_koii/namespace-wrapper";
import { Submission } from "@_koii/namespace-wrapper/dist/types";

const getSubmissionList = async (roundNumber: number): Promise<Record<string, Submission>> => {
  const submissionInfo = await namespaceWrapper.getTaskSubmissionInfo(roundNumber);
  return submissionInfo?.submissions[roundNumber] || {};
};

export const getEmptyDistributionList = async (submitters: Submitter[]): Promise<DistributionList> => {
  const distributionList: DistributionList = {};
  for (const submitter of submitters) {
    distributionList[submitter.publicKey] = 0;
  }
  return distributionList;
};

export const distribution = async (
  submitters: Submitter[],
  bounty: number,
  roundNumber: number,
): Promise<DistributionList> => {
  try {
    const distributionList: DistributionList = {};
    const eligibleSubmitters = [];

    for (const submitter of submitters) {
      console.log(`\n[DISTRIBUTION] Processing submitter: ${submitter.publicKey}`);

      console.log(`[DISTRIBUTION] Getting submission list for round ${roundNumber}`);
      const submitterSubmissions = await getSubmissionList(roundNumber);
      console.log(`[DISTRIBUTION] Total submissions found: ${Object.keys(submitterSubmissions).length}`);

      const submitterSubmission = submitterSubmissions[submitter.publicKey];
      if (!submitterSubmission || submitterSubmission.submission_value === "submission") {
        console.log(`[DISTRIBUTION] ❌ No valid submission found for submitter ${submitter.publicKey}`);
        distributionList[submitter.publicKey] = 0;
        continue;
      } else {
        if (submitter.votes > 0) {
          eligibleSubmitters.push(submitter);
        } else {
          distributionList[submitter.publicKey] = 0;
        }
      }
    }
    for (const submitter of eligibleSubmitters) {
      distributionList[submitter.publicKey] = Math.floor(bounty / eligibleSubmitters.length);
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
