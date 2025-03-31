import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";
import { getLeaderNode } from "../utils/leader";
import { getExistingIssues } from "../utils/existingIssues";
interface PodCallBody {
  taskId: string;
  roundNumber: number;
  stakingKey: string;
  pubKey: string;
  stakingSignature: string;
  publicSignature: string;
  repoOwner: string;
  repoName: string;
  distributionList: Record<string, any>;
}

interface Submission {
  stakingKey: string;
  prUrl?: string;
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

    // await orcaClient.podCall(`create-aggregator-repo/${roundNumber + 1}`, {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json",
    //   },
    //   // TODO: Change to dynamic repo owner and name by checking the middle server
    //   body: JSON.stringify({ taskId: TASK_ID, repoOwner: "koii-network", repoName: "builder-test" }),
    // });

    const stakingKeypair = await namespaceWrapper.getSubmitterAccount();
    if (!stakingKeypair) {
      throw new Error("No staking keypair found");
    }
    const stakingKey = stakingKeypair.publicKey.toBase58();
    // const pubKey = await namespaceWrapper.getMainAccountPubkey();
    // if (!pubKey) {
    //   throw new Error("No public key found");
    // }

    const existingIssues = await getExistingIssues();
    if (existingIssues.length == 0) {
      namespaceWrapper.storeSet(`result-${roundNumber}`, "False");
      return;
    } else {
      namespaceWrapper.storeSet(`result-${roundNumber}`, "True");
    }
    const { isLeader, leaderNode } = await getLeaderNode({
      roundNumber,
      leaderNumber: 1,
      submitterPublicKey: stakingKey,
    });
    console.log({ isLeader, leaderNode });
    if (leaderNode === null) {
      return;
    }

  } catch (error) {
    console.error("EXECUTE TASK ERROR:", error);
  }
}
