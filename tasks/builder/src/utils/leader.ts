import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import { getFile } from "./ipfs";
import seedrandom from "seedrandom";

export async function fetchRoundSubmissionGitHubRepoOwner(
  roundNumber: number,
  submitterPublicKey: string,
): Promise<string | null> {
  try{
    const taskSubmissionInfo = await namespaceWrapper.getTaskSubmissionInfo(roundNumber);
    if (!taskSubmissionInfo) {
      console.error("NO TASK SUBMISSION INFO");
      return null;
    }
  const submissions = taskSubmissionInfo.submissions;
  // This should only have one round
  const lastRound = Object.keys(submissions).pop();
  if (!lastRound) {
    return null;
  }
  const lastRoundSubmissions = submissions[lastRound];
  const lastRoundSubmitterSubmission = lastRoundSubmissions[submitterPublicKey];
  console.log("lastRoundSubmitterSubmission", { lastRoundSubmitterSubmission });
  if (!lastRoundSubmitterSubmission) {
    return null;
  }
  const cid = lastRoundSubmitterSubmission.submission_value;
  const submissionString = await getFile(cid);
  const submission = JSON.parse(submissionString);
  console.log({ submission });

  // verify the signature of the submission
  const signaturePayload = await namespaceWrapper.verifySignature(submission.signature, submitterPublicKey);

  console.log({ signaturePayload });

  // verify the signature payload
  if (signaturePayload.error || !signaturePayload.data) {
    console.error("INVALID SIGNATURE");
    return null;
  }
  const data = JSON.parse(signaturePayload.data);

  if (
    data.taskId !== TASK_ID ||
    data.stakingKey !== submitterPublicKey
  ) {
    console.error("INVALID SIGNATURE DATA");
    return null;
  }
  if (!data.githubUsername) {
    console.error("NO GITHUB USERNAME");
    console.log("data", { data });
    return null;
    }
    return data.githubUsername;
  } catch (error) {
    console.error("FETCH LAST ROUND SUBMISSION GITHUB REPO OWNER ERROR:", error);
    return null;
  }
}

export async function selectShortestDistance(keys: string[]): Promise<string> {
  const submitterAccount = await namespaceWrapper.getSubmitterAccount();
  if (!submitterAccount) {
    throw new Error("No submitter account found");
  }
  const submitterPublicKey = submitterAccount.publicKey.toBase58();
  let shortestDistance = Infinity;
  let closestKey = "";
  for (const key of keys) {
    const distance = knnDistance(submitterPublicKey, key);
    if (distance < shortestDistance) {
      shortestDistance = distance;
      closestKey = key;
    }
  }
  return closestKey;
}
// @deprecated
function levenshteinDistance(a: string, b: string): number {
  const matrix = Array.from({ length: a.length + 1 }, () => Array(b.length + 1).fill(0));

  for (let i = 0; i <= a.length; i++) {
    matrix[i][0] = i;
  }
  for (let j = 0; j <= b.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1, // delete
        matrix[i][j - 1] + 1, // insert
        matrix[i - 1][j - 1] + cost, // replace
      );
    }
  }

  return matrix[a.length][b.length];
}
export async function getLeaderNode(roundNumber: number, leaderNumber: number = 5): Promise<{isLeader: boolean, leaderNode: string}> {
  // If it is the first round, return the default leader node
  if (roundNumber <= 1) {
    return {isLeader: false, leaderNode: "koii-network"};
  }
  const submissionPublicKeysFrequency: Record<string, number> = {};
  const submissionAuditTriggerKeys = new Set<string>();
  for (let i = 1; i < 5; i++) {
    // Try is to avoid error when roundNumber <= 4
    try {
      const taskSubmissionInfo = await namespaceWrapper.getTaskSubmissionInfo(roundNumber - i);
      if (taskSubmissionInfo) {
        const submissions = taskSubmissionInfo.submissions;
        for (const round in submissions) {
          for (const publicKey in submissions[round]) {
            if (submissionPublicKeysFrequency[publicKey]) {
              submissionPublicKeysFrequency[publicKey]++;
            } else {
              submissionPublicKeysFrequency[publicKey] = 1;
            }
          }
        }

        // Handle the audit trigger
        const submissionAuditTrigger = taskSubmissionInfo.submissions_audit_trigger;
        for (const round in submissionAuditTrigger) {
          for (const publicKey in submissionAuditTrigger[round]) {
            submissionAuditTriggerKeys.add(publicKey);
          }
        }
      }
    } catch (error) {
      console.error("GET LEADER NODE ERROR:", error);
    }
  }

  // Get all the keys not in submissionAuditTriggerKeys; and sort them by frequency
  const keysNotInAuditTrigger = Object.keys(submissionPublicKeysFrequency).filter(
    (key) => !submissionAuditTriggerKeys.has(key),
  );
  const sortedKeys = keysNotInAuditTrigger.sort(
    (a, b) => submissionPublicKeysFrequency[b] - submissionPublicKeysFrequency[a],
  );
  // If the number of top frequency keys is less than leaderNumber, return the default leader node
  if (sortedKeys.length < leaderNumber) {
    return {isLeader: false, leaderNode: "koii-network"};
  }
  // Top value in sortedKeys
  const topValue = sortedKeys[leaderNumber - 1];
  // Count how many keys have the same value as topValue
  const count = sortedKeys.filter(
    (key) => submissionPublicKeysFrequency[key] === submissionPublicKeysFrequency[topValue],
  ).length;
  // If the count is greater than or equal to leaderNumber, return the top value
  let chosenKey = "";
  if (count >= leaderNumber) {
    // select the random 5 with seed
    const rng = seedrandom(String(TASK_ID));
    const randomKeys = sortedKeys.sort(() => rng() - 0.5).slice(0, leaderNumber);
    console.log("randomKeys", { randomKeys });
    const shortestDistanceKey = await selectShortestDistance(randomKeys);
    console.log("shortestDistanceKey", { shortestDistanceKey });
    chosenKey = shortestDistanceKey;
  } else {
    chosenKey = sortedKeys[leaderNumber - 1];
  }
  console.log("chosenKey", { chosenKey });
  // else random with Seed
  const submitterAccount = await namespaceWrapper.getSubmitterAccount();
  if (!submitterAccount) {
    throw new Error("No submitter account found");
  }
  const submitterPublicKey = submitterAccount.publicKey.toBase58();
  if (chosenKey == submitterPublicKey) {
    return {isLeader: true, leaderNode: "koii-network"};
  }
  // This start with the current round
  for (let i = 1; i < 5; i++) {
    const githubUsername = await fetchRoundSubmissionGitHubRepoOwner(roundNumber - i, chosenKey);
    if (githubUsername) {
      return {isLeader: false, leaderNode: githubUsername};
    }
  }
  return {isLeader: false, leaderNode: "koii-network"};
}

function base58ToNumber(char: string): number {
  const base58Chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
  return base58Chars.indexOf(char);
}

function knnDistance(a: string, b: string): number {
  if (a.length !== b.length) {
    throw new Error("Strings must be of the same length for KNN distance calculation.");
  }
  const truncatedA = a.slice(0, 30);
  const truncatedB = b.slice(0, 30);

  let distance = 0;
  for (let i = 0; i < truncatedA.length; i++) {
    const numA = base58ToNumber(truncatedA[i]);
    const numB = base58ToNumber(truncatedB[i]);
    distance += Math.abs(numA - numB);
  }

  return distance;
}

// async function test(){
//   const keypair = Keypair.generate();
//   const publicKey = keypair.publicKey.toBase58();
//   // wait 5 seconds
//   await new Promise(resolve => setTimeout(resolve, 5000));

//   const publicKey2 = "8JEYBpXFgYx4iEWNsL1SD7m1RS6VdfrFq7nNY2rfUhTk"
//   const distance = knnDistance(publicKey, publicKey2);
//   console.log(publicKey);
//   console.log(publicKey2);
//   console.log(distance);
// }

// test();
