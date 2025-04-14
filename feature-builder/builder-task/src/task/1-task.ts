import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import { triggerAuditUpdate } from "../utils/auditUpdate";
import { createAggregatorRepo } from "../utils/aggregatorRepo";
import "dotenv/config";

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

    // Once we reach round 4, trigger the audit update to check the distribution list
    // the distribution list should be available after round 3 but sometimes it's not in the task state yet
    // so we wait one additional round
    if (roundNumber >= 4) {
      await triggerAuditUpdate(TASK_ID || "", roundNumber - 4, stakingKeypair, orcaClient);
    }

    const leaderPrUrl = await runTask(roundNumber, "leader", orcaClient, stakingKey, pubKey, stakingKeypair.secretKey);
    if (!leaderPrUrl) {
      const workerPrUrl = await runTask(
        roundNumber,
        "worker",
        orcaClient,
        stakingKey,
        pubKey,
        stakingKeypair.secretKey,
      );
      if (!workerPrUrl) {
        console.log("Did not create PR for round", roundNumber);
      }
    }
  } catch (error) {
    console.error("EXECUTE TASK ERROR:", error);
  }
}

async function runTask(
  roundNumber: number,
  taskType: "worker" | "leader",
  orcaClient: any,
  stakingKey: string,
  pubKey: string,
  secretKey: Uint8Array,
) {
  try {
    const taskConfig = {
      worker: {
        fetchAction: "fetch-todo",
        addAction: "add-todo-pr",
        endpoint: `worker-task/${roundNumber}`,
      },
      leader: {
        fetchAction: "fetch-issue",
        addAction: "add-issue-pr",
        endpoint: `leader-task/${roundNumber}`,
      },
    };
    const fetchTodoPayload = {
      taskId: TASK_ID,
      roundNumber,
      githubUsername: process.env.GITHUB_USERNAME,
      stakingKey,
      pubKey,
      action: taskConfig[taskType].fetchAction,
    };
    const addPRPayload = {
      taskId: TASK_ID,
      roundNumber,
      githubUsername: process.env.GITHUB_USERNAME,
      stakingKey,
      pubKey,
      action: taskConfig[taskType].addAction,
    };

    const stakingSignature = await namespaceWrapper.payloadSigning(fetchTodoPayload, secretKey);
    const publicSignature = await namespaceWrapper.payloadSigning(fetchTodoPayload);
    const addPRSignature = await namespaceWrapper.payloadSigning(addPRPayload, secretKey);

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

    const response = await orcaClient.podCall(taskConfig[taskType].endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(podCallBody),
    });

    if (response?.data?.success) {
      return response.data.pr_url;
    } else {
      console.error(`${taskType} task failed:`, response?.data?.error || "Unknown error");
      return null;
    }
  } catch (error) {
    console.error(`${taskType} task error:`, error);
    return null;
  }
}
