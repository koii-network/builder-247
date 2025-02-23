import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import "dotenv/config";

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

    const signature = await namespaceWrapper.payloadSigning(
      {
        taskId: TASK_ID,
        roundNumber,
        githubUsername: process.env.GITHUB_USERNAME,
        stakingKey,
        pubKey,
        action: "fetch",
      },
      stakingKeypair.secretKey,
    );

    orcaClient
      .podCall(`task/${roundNumber}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          taskId: TASK_ID,
          roundNumber,
          stakingKey,
          pubKey,
          signature,
        }),
      })
      .then((result: any) => {
        const prUrl = result.data.prUrl;
        if (!prUrl) {
          throw new Error("No PR URL found");
        }
        namespaceWrapper.getSubmitterAccount().then((stakingKeypair) => {
          if (!stakingKeypair) {
            throw new Error("No staking keypair found");
          }
          const stakingKey = stakingKeypair.publicKey.toBase58();
          namespaceWrapper
            .payloadSigning(
              {
                taskId: TASK_ID,
                roundNumber,
                prUrl,
                stakingKey,
                pubKey,
                action: "add",
              },
              stakingKeypair.secretKey,
            )
            .then((signature) => {
              orcaClient
                .podCall(`submit-pr/${roundNumber}`, {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify({
                    signature,
                    stakingKey,
                    pubKey,
                    prUrl,
                  }),
                })
                .then((result: any) => {
                  console.log(`${roundNumber} task result: ${result.data.message}`);
                })
                .catch((error: any) => {
                  console.error("EXECUTE TASK ERROR:", error);
                });
            });
        });
      })
      .catch((error: any) => {
        console.error("EXECUTE TASK ERROR:", error);
      });
  } catch (error) {
    console.error("EXECUTE TASK ERROR:", error);
  }
}
