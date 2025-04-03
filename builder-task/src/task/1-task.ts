import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getLeaderNode } from "../utils/leader";

interface PodCallBody {
  taskId: string;
  roundNumber: number;
  stakingKey: string;
  pubKey: string;
  stakingSignature: string;
  publicSignature: string;
  addPRSignature: string;
}

/**
 * Function to trigger the update-audit-result endpoint to update todo and issue statuses
 * This will update todos that were approved in audits and make issues ready for leader round
 */
async function triggerAuditUpdate(taskId: string, round: number, stakingKeypair: any): Promise<void> {
  try {
    console.log(`Triggering audit update for worker round ${round}`);
    const orcaClient = await getOrcaClient();
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();

    // Create the payload for the update-audit-result endpoint
    const updatePayload = {
      taskId,
      round,
      action: "update-audit-result",
      stakingKey,
      pubKey,
      githubUsername: process.env.GITHUB_USERNAME,
    };

    // Sign the payload
    const signature = await namespaceWrapper.payloadSigning(updatePayload, stakingKeypair.secretKey);

    // Make the request
    const response = await orcaClient.podCall(`update-audit-result`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        taskId,
        round,
        signature,
        stakingKey,
        pubKey,
      }),
    });

    console.log("Audit update response:", response);
  } catch (error) {
    console.error("Error triggering audit update:", error);
  }
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

    const repoData = await orcaClient.podCall(`create-aggregator-repo/${TASK_ID}`, {
      method: "POST",
    });

    if (!repoData.success) {
      console.error("Failed to create aggregator repo", repoData.error);
      return;
    }

    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    const pubKey = await namespaceWrapper.getMainAccountPubkey();
    if (!pubKey) {
      throw new Error("No public key found");
    }

    const aggregatorPayload = {
      taskId: TASK_ID,
      roundNumber,
      githubUsername: process.env.GITHUB_USERNAME,
      stakingKey,
      pubKey,
      action: "create-repo",
      issueUuid: repoData.data.branch_name,
      aggregatorUrl: repoData.data.fork_url,
    };
    const aggregatorSignature = await namespaceWrapper.payloadSigning(aggregatorPayload, stakingKeypair.secretKey);

    const aggregatorPodCallBody = {
      stakingKey,
      pubKey,
      signature: aggregatorSignature,
    };

    await orcaClient.podCall(`add-aggregator-info/${TASK_ID}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(aggregatorPodCallBody),
    });

    const { isLeader, leaderNode } = await getLeaderNode({
      roundNumber,
      leaderNumber: 1,
      submitterPublicKey: stakingKey,
    });
    console.log({ isLeader, leaderNode });
    if (leaderNode === null) {
      return;
    }

    // If this is a leader task and round >= 4, call update-audit-result for the previous worker round
    if (roundNumber >= 3) {
      await triggerAuditUpdate(TASK_ID || "", roundNumber - 3, stakingKeypair);
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
