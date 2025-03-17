interface Submission {
  stakingKey: string;
  prUrl?: string;
}

/**
 * Filter out ineligible nodes from the distribution list
 * @param distributionList Raw distribution list from namespace
 * @param submissions List of submissions for the round
 * @returns Filtered distribution list containing only eligible nodes
 */
export async function filterIneligibleNodes(
  distributionList: Record<string, number>,
  submissions: Submission[],
): Promise<Record<string, number>> {
  const filteredDistributionList: Record<string, number> = {};

  for (const [stakingKey, amount] of Object.entries(distributionList)) {
    const numericAmount = amount as number;

    // Skip if amount is zero or negative (failed audit)
    if (numericAmount <= 0) {
      console.log(`Skipping staking key ${stakingKey} due to zero/negative reward: ${numericAmount}`);
      continue;
    }

    // Find corresponding submission
    const submission = submissions.find((s) => s.stakingKey === stakingKey);

    // Skip if no submission found
    if (!submission) {
      console.log(`Skipping staking key ${stakingKey} - no submission found`);
      continue;
    }

    // Skip if submission has no PR URL or is a dummy submission
    if (!submission.prUrl || submission.prUrl === "none") {
      console.log(`Skipping staking key ${stakingKey} - no valid PR URL`);
      continue;
    }

    // Node is eligible, include in filtered list
    filteredDistributionList[stakingKey] = numericAmount;
    console.log(`Including eligible node ${stakingKey} with amount ${numericAmount}`);
  }

  const origCount = Object.keys(distributionList).length;
  const filteredCount = Object.keys(filteredDistributionList).length;
  console.log(
    `Filtered distribution list from ${origCount} to ${filteredCount} nodes after filtering ineligible nodes`,
  );

  return filteredDistributionList;
}
