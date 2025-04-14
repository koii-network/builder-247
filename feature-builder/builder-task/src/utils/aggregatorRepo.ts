import { TASK_ID, namespaceWrapper } from "@_koii/namespace-wrapper";

export async function createAggregatorRepo(
  orcaClient: any,
  roundNumber: number,
  stakingKey: string,
  pubKey: string,
  secretKey: Uint8Array<ArrayBufferLike>,
): Promise<void> {
  try {
    const repoResult = await orcaClient.podCall(`create-aggregator-repo/${TASK_ID}`, {
      method: "POST",
    });

    const repoData = repoResult.data;

    if (!repoData.success) {
      console.error("Failed to create aggregator repo", repoData.error);
      return;
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
    const aggregatorSignature = await namespaceWrapper.payloadSigning(aggregatorPayload, secretKey);

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
  } catch (error) {
    console.error("Error in createAggregatorRepo:", error);
  }
}
