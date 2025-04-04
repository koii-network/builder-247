import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getLeaderNode } from "../utils/leader";
import { triggerAuditUpdate } from "../utils/auditUpdate";
import { createAggregatorRepo } from "../utils/aggregatorRepo";

interface PodCallBody {
  taskId: string;
  roundNumber: number;
  stakingKey: string;
  pubKey: string;
  stakingSignature: string;
  publicSignature: string;
  addPRSignature: string;
}

export async function task(roundNumber: number): Promise<void> {
  /**
   * Run your task and store the proofs to be submitted for auditing
   * It is expected you will store the proofs in your container
   * The submission of the proofs is done in the submission function
   */
  console.log(`EXECUTE TASK FOR ROUND ${roundNumber}`);
  try {
    const orcaClient = await getOrcaClient();
    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }

    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    if (!pubKey) {
      throw new Error("No public key found");
    }

    await createAggregatorRepo(orcaClient, roundNumber, stakingKey, pubKey, stakingKeypair.secretKey);

    const { isLeader, leaderNode } = await getLeaderNode({
      roundNumber,
      leaderNumber: 1,
      submitterPublicKey: stakingKey,
    });
    console.log({ isLeader, leaderNode });
    if (leaderNode === null) {
      return;
    }

    // Once we reach round 3, trigger the audit update for the previous round to check the distribution list
    if (roundNumber >= 3) {
      await triggerAuditUpdate(TASK_ID || "", roundNumber - 3, stakingKeypair, orcaClient);
    }

    const fetchTodoPayload = {
      taskId: TASK_ID,
      roundNumber,
      githubUsername: process.env.GITHUB_USERNAME,
      stakingKey,
      pubKey,
      action: isLeader ? "fetch-todo" : "fetch-issue",
    };
    const addPRPayload = {
      taskId: TASK_ID,
      roundNumber,
      githubUsername: process.env.GITHUB_USERNAME,
      stakingKey,
      pubKey,
      action: isLeader ? "add-todo-pr" : "add-issue-pr",
    };
    const stakingSignature = await namespaceWrapper.payloadSigning(fetchTodoPayload, stakingKeypair.secretKey);
    const publicSignature = await namespaceWrapper.payloadSigning(fetchTodoPayload);
    const addPRSignature = await namespaceWrapper.payloadSigning(addPRPayload, stakingKeypair.secretKey);

    if (!stakingSignature || !publicSignature || !addPRSignature) {
      throw new Error("Signature generation failed");
    }

    const podCallBody: PodCallBody = {
      taskId: TASK_ID!,
      roundNumber,
      stakingKey,
      pubKey,
      stakingSignature,
      publicSignature,
      addPRSignature,
    };
    let podCallUrl;
    if (isLeader) {
      podCallUrl = `leader-task/${roundNumber}`;
    } else {
      podCallUrl = `worker-task/${roundNumber}`;
    }

    await orcaClient.podCall(podCallUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(podCallBody),
    });
  } catch (error) {
    console.error("EXECUTE TASK ERROR:", error);
  }
}
