async function verifySignatureData(
  signature: string,
  stakingKey: string,
  pubKey: string,
  action: string,
): Promise<{
  roundNumber: number;
  githubUsername: string;
  issueUuid: string;
  aggregatorUrl: string;
  taskId: string;
} | null> {
  try {
    const { data, error } = await verifySignature(signature, stakingKey);
    if (error || !data) {
      console.log("bad signature");
      return null;
    }
    const body = JSON.parse(data);
    console.log({ signature_payload: body });
    console.log("task id matches", taskIDs.includes(body.taskId));
    console.log("round number is number", typeof body.roundNumber === "number");
    console.log("pub key matches", body.pubKey === pubKey);
    console.log("staking key matches", body.stakingKey === stakingKey);
    console.log("action matches", body.action === action);
    console.log("github username exists", body.githubUsername);
    console.log("issue uuid exists", body.issueUuid);
    console.log("aggregator url exists", body.aggregatorUrl);
    if (
      !body.taskId ||
      typeof body.roundNumber !== "number" ||
      !taskIDs.includes(body.taskId) ||
      body.action !== action ||
      !body.githubUsername ||
      !body.pubKey ||
      body.pubKey !== pubKey ||
      !body.stakingKey ||
      body.stakingKey !== stakingKey ||
      !body.issueUuid ||
      !body.aggregatorUrl
    ) {
      console.log("bad signature data");
      return null;
    }
    return {
      roundNumber: body.roundNumber,
      githubUsername: body.githubUsername,
      issueUuid: body.issueUuid,
      aggregatorUrl: body.aggregatorUrl,
      taskId: body.taskId,
    };
  } catch (error) {
    console.log("unexpected signature error", error);
    return null;
  }
}

export const addAggregatorInfo = async (req: Request, res: Response) => {
  const requestBody = verifyRequestBody(req);
  if (!requestBody) {
    res.status(401).json({
      success: false,
      message: "Invalid request body",
    });
    return;
  }

  const signatureData = await verifySignatureData(
    requestBody.signature,
    requestBody.stakingKey,
    requestBody.pubKey,
    "create-repo",
  );
  if (!signatureData) {
    res.status(401).json({
      success: false,
      message: "Failed to verify signature",
    });
    return;
  }

  const response = await addAggregatorInfoLogic(requestBody, signatureData);
  res.status(response.statuscode).json(response.data);
};

export const addAggregatorInfoLogic = async (
  requestBody: { signature: string; stakingKey: string; pubKey: string; issueUuid: string; aggregatorUrl: string },
  signatureData: { roundNumber: number; githubUsername: string; issueUuid: string; aggregatorUrl: string },
) => {
  console.log("Searching for issue with:", {
    issueUuid: signatureData.issueUuid,
  });
  const issue = await IssueModel.findOneAndUpdate(
    {
      issueUuid: signatureData.issueUuid,
    },
    {
      $set: {
        status: IssueStatus.IN_PROCESS,
        aggregatorName: signatureData.githubUsername,
        aggregatorUrl: signatureData.aggregatorUrl,
      },
    },
    { new: true },
  );
  if (!issue) {
    return {
      statuscode: 404,
      data: {
        success: false,
        message: "Issue not found",
      },
    };
  }

  issue.status = IssueStatus.IN_PROCESS;

  await issue.save();

  return {
    statuscode: 200,
    data: {
      success: true,
      message: "Aggregator info added",
    },
  };
};
