import { Submitter, DistributionList } from "@_koii/task-manager";


export const distribution = async (
  submitters: Submitter[],
  bounty: number,
  roundNumber: number
): Promise<DistributionList> => {
  /**
   * Generate the reward list for a given round
   * This function should return an object with the public keys of the submitters as keys
   * and the reward amount as values
   */
  console.log(`MAKE DISTRIBUTION LIST FOR ROUND ${roundNumber}`);
  const distributionList: DistributionList = {};
  const approvedSubmitters = [];
  // Slash the stake of submitters who submitted incorrect values
  // and make a list of submitters who submitted correct values
  for (const submitter of submitters) {
    if (submitter.votes <= 0) {
      distributionList[submitter.publicKey] = 0;
    } else {
      approvedSubmitters.push(submitter.publicKey);
    }
  }
  if (approvedSubmitters.length === 0) {
    console.log("NO NODES TO REWARD");
    return distributionList;
  }
  // reward the submitters who submitted correct values
  const reward = Math.floor(bounty / approvedSubmitters.length);
  console.log("REWARD PER NODE", reward);
  approvedSubmitters.forEach((candidate) => {
    distributionList[candidate] = reward;
  });
  return distributionList;
}
