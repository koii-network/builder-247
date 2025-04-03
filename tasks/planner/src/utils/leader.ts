import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import { getFile } from "./ipfs";
import seedrandom from "seedrandom";

export async function fetchRoundSubmissionGitHubRepoOwner(
  roundNumber: number,
  submitterPublicKey: string,
): Promise<string | null> {
  try {
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

    if (data.taskId !== TASK_ID || data.stakingKey !== submitterPublicKey) {
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

export async function selectShortestDistance(keys: string[], submitterPublicKey: string): Promise<string> {
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

async function getSubmissionInfo(roundNumber: number): Promise<any> {
  try {
    return await namespaceWrapper.getTaskSubmissionInfo(roundNumber);
  } catch (error) {
    console.error("GET SUBMISSION INFO ERROR:", error);
    return null;
  }
}

function calculatePublicKeyFrequency(submissions: any): Record<string, number> {
  const frequency: Record<string, number> = {};
  for (const round in submissions) {
    for (const publicKey in submissions[round]) {
      if (frequency[publicKey]) {
        frequency[publicKey]++;
      } else {
        frequency[publicKey] = 1;
      }
    }
  }
  return frequency;
}

function handleAuditTrigger(submissionAuditTrigger: any): Set<string> {
  const auditTriggerKeys = new Set<string>();
  for (const round in submissionAuditTrigger) {
    for (const publicKey in submissionAuditTrigger[round]) {
      auditTriggerKeys.add(publicKey);
    }
  }
  return auditTriggerKeys;
}

async function selectLeaderKey(
  sortedKeys: string[],
  leaderNumber: number,
  submitterPublicKey: string,
  submissionPublicKeysFrequency: Record<string, number>,
): Promise<string> {
  const topValue = sortedKeys[leaderNumber - 1];
  const count = sortedKeys.filter(
    (key) => submissionPublicKeysFrequency[key] >= submissionPublicKeysFrequency[topValue],
  ).length;

  if (count >= leaderNumber) {
    const rng = seedrandom(String(TASK_ID));
    const guaranteedKeys = sortedKeys.filter(
      (key) => submissionPublicKeysFrequency[key] > submissionPublicKeysFrequency[topValue],
    );
    const randomKeys = sortedKeys
      .filter((key) => submissionPublicKeysFrequency[key] === submissionPublicKeysFrequency[topValue])
      .sort(() => rng() - 0.5)
      .slice(0, leaderNumber - guaranteedKeys.length);
    const keys = [...guaranteedKeys, ...randomKeys];
    return await selectShortestDistance(keys, submitterPublicKey);
  } else {
    const keys = sortedKeys.slice(0, leaderNumber);
    return await selectShortestDistance(keys, submitterPublicKey);
  }
}
export async function getRandomNodes(roundNumber: number, numberOfNodes: number): Promise<string[]> {
  console.log("Getting random nodes for round:", roundNumber, "with number of nodes:", numberOfNodes);
  const lastRoundSubmission = await getSubmissionInfo(roundNumber - 1);
  console.log("Last round submission:", lastRoundSubmission);
  if (!lastRoundSubmission) {
    return [];
  }

  const lastRoundSubmissions = lastRoundSubmission.submissions;
  console.log("Last round submissions:", lastRoundSubmissions);
  
  // Get the last round number
  const lastRound = Object.keys(lastRoundSubmissions).pop();
  if (!lastRound) {
    return [];
  }
  
  // Get the submissions for that round
  const submissions = lastRoundSubmissions[lastRound];
  console.log("Submissions:", submissions);
  const availableKeys = Object.keys(submissions);
  console.log("Available keys:", availableKeys);
  // If we have fewer submissions than requested nodes, return all available submissions
  if (availableKeys.length <= numberOfNodes) {
    return availableKeys;
  }
  
  const seed = TASK_ID + roundNumber.toString() || "default" + roundNumber;
  const rng = seedrandom(seed);
  // Use the keys from the submissions object
  const randomKeys = availableKeys.sort(() => rng() - 0.5).slice(0, numberOfNodes);
  
  console.log("Random keys:", randomKeys);
  return randomKeys;
}

// Helper function that finds the leader for a specific round
async function getLeaderForRound(
  roundNumber: number,
  maxLeaderNumber: number,
  submitterPublicKey: string,
): Promise<{ chosenKey: string | null; leaderNode: string | null }> {
  if (roundNumber <= 0) {
    return { chosenKey: null, leaderNode: null };
  }

  const submissionPublicKeysFrequency: Record<string, number> = {};
  const submissionAuditTriggerKeys = new Set<string>();

  for (let i = 1; i < 5; i++) {
    const taskSubmissionInfo = await getSubmissionInfo(roundNumber - i);
    console.log({ taskSubmissionInfo });
    if (taskSubmissionInfo) {
      const submissions = taskSubmissionInfo.submissions;
      const frequency = calculatePublicKeyFrequency(submissions);
      Object.assign(submissionPublicKeysFrequency, frequency);

      const auditTriggerKeys = handleAuditTrigger(taskSubmissionInfo.submissions_audit_trigger);
      auditTriggerKeys.forEach((key) => submissionAuditTriggerKeys.add(key));
    }
  }

  const keysNotInAuditTrigger = Object.keys(submissionPublicKeysFrequency).filter(
    (key) => !submissionAuditTriggerKeys.has(key),
  );
  const sortedKeys = keysNotInAuditTrigger.sort(
    (a, b) => submissionPublicKeysFrequency[b] - submissionPublicKeysFrequency[a],
  );

  console.log({ sortedKeys });

  let chosenKey = null;

  const leaderNumber = sortedKeys.length < maxLeaderNumber ? sortedKeys.length : maxLeaderNumber;

  chosenKey = await selectLeaderKey(sortedKeys, leaderNumber, submitterPublicKey, submissionPublicKeysFrequency);

  // Find GitHub username for the chosen key
  for (let i = 1; i < 5; i++) {
    const githubUsername = await fetchRoundSubmissionGitHubRepoOwner(roundNumber - i, chosenKey);
    if (githubUsername) {
      return { chosenKey, leaderNode: githubUsername };
    }
  }

  return { chosenKey, leaderNode: null };
}

export async function getLeaderNode({
  roundNumber,
  leaderNumber = 5,
  submitterPublicKey,
}: {
  roundNumber: number;
  leaderNumber?: number;
  submitterPublicKey: string;
}): Promise<{ isLeader: boolean; leaderNode: string | null }> {
  // Find leader for current round
  const currentLeader = await getLeaderForRound(roundNumber, leaderNumber, submitterPublicKey);
  console.log({ currentLeader });

  if (currentLeader.chosenKey === submitterPublicKey) {
    // If we're the leader, get the leader from 3 rounds ago
    const previousLeader = await getLeaderForRound(roundNumber - 3, leaderNumber, submitterPublicKey);
    console.log({ previousLeader });
    return { isLeader: true, leaderNode: previousLeader.leaderNode };
  }

  // Not the leader, return the current leader's info
  return { isLeader: false, leaderNode: currentLeader.leaderNode };
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
