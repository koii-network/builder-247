import { namespaceWrapper } from "@_koii/namespace-wrapper";
import { getFile } from "./ipfs";

/**
 * Filter out ineligible nodes from the distribution list
 * @param distributionList Raw distribution list from namespace
 * @param submissions List of submissions for the round
 * @returns Filtered distribution list containing only eligible nodes
 */
async function filterIneligibleNodes(
  distributionList: Record<string, number>,
  roundNumber: number,
): Promise<Record<string, any>> {
  const filteredDistributionList: Record<string, any> = {};

  if (Object.keys(distributionList).length === 0) {
    console.log("Distribution list is empty, skipping filterIneligibleNodes");
    return filteredDistributionList;
  }

  const taskSubmissionInfo = await namespaceWrapper.getTaskSubmissionInfo(roundNumber);
  if (!taskSubmissionInfo) {
    console.log("Task submission info is null, skipping filterIneligibleNodes");
    return filteredDistributionList;
  }

  const submissions = taskSubmissionInfo.submissions;

  for (const [stakingKey, amount] of Object.entries(distributionList)) {
    const numericAmount = amount as number;

    // Skip if amount is zero or negative (failed audit)
    if (numericAmount <= 0) {
      console.log("Skipping staking key:", stakingKey, "Amount:", numericAmount);
      continue;
    }

    // Find corresponding submission
    const submissionCID = submissions[roundNumber][stakingKey]["submission_value"];

    const submission = await getFile(submissionCID);

    // Skip if no submission found
    if (!submission) {
      console.log("No submission found, skipping staking key:", stakingKey);
      continue;
    }

    const submissionData = JSON.parse(submission);

    console.log("Staking key:", stakingKey, "Submission data:", submissionData);

    const payload = await namespaceWrapper.verifySignature(submissionData.signature, stakingKey);
    console.log("Payload:", payload);

    const payloadData = JSON.parse(payload.data || "{}");

    // Skip if submission has no PR URL or is a dummy submission
    if (!payloadData.prUrl || payloadData.prUrl === "none") {
      continue;
    }

    // Node is eligible, include in filtered list
    filteredDistributionList[stakingKey] = payloadData;
  }

  console.log("Filtered distribution list:", filteredDistributionList);

  return filteredDistributionList;
}

export async function getDistributionList(roundNumber: number): Promise<Record<string, any> | null> {
  try {
    const taskDistributionInfo = await namespaceWrapper.getTaskDistributionInfo(roundNumber);
    if (!taskDistributionInfo) {
      console.log("Task distribution info is null, skipping task");
      return null;
    }
    const distribution = taskDistributionInfo.distribution_rewards_submission[roundNumber];
    const leaderStakingKey = Object.keys(distribution)[0];
    console.log("Fetching distribution list for round", roundNumber, "with leader staking key", leaderStakingKey);
    const distributionList = await namespaceWrapper.getDistributionList(leaderStakingKey, roundNumber);
    if (!distributionList) {
      console.log("Distribution list is null, skipping task");
      return null;
    }
    console.log("Raw distribution list:", distributionList);

    const parsedDistributionList: Record<string, number> = JSON.parse(distributionList);

    return await filterIneligibleNodes(parsedDistributionList, roundNumber);
  } catch (error) {
    console.error("Error fetching distribution list:", error);
    return null;
  }
}
