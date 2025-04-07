import { TASK_ID } from "@_koii/namespace-wrapper";
import { getFile } from "./ipfs";
import { Submission } from "@_koii/namespace-wrapper/dist/types";
import { Submitter } from "@_koii/task-manager/dist/types/global";
import { namespaceWrapper } from "@_koii/namespace-wrapper";
export async function submissionJSONSignatureDecode({submission_value, submitterPublicKey, roundNumber}: {submission_value: string, submitterPublicKey: string, roundNumber: number}) {
    let submissionString;
    try {
        console.log("Getting file from IPFS", submission_value);
      submissionString = await getFile(submission_value);
      console.log("submissionString", submissionString);
    } catch (error) {

      console.log("error", error);
      console.error("INVALID SIGNATURE DATA");
      return null;
    }
    // verify the signature of the submission
    const submission = JSON.parse(submissionString);
    console.log("submission", submission);
    const signaturePayload = await namespaceWrapper.verifySignature(submission.signature, submitterPublicKey);
    if (!signaturePayload.data) {
      console.error("INVALID SIGNATURE");
      return null;
    }
    const data = JSON.parse(signaturePayload.data);
    console.log("signaturePayload", signaturePayload);
    console.log("data", data);
    if (
      data.taskId !== TASK_ID ||
      data.roundNumber !== roundNumber ||
      data.stakingKey !== submitterPublicKey ||
      !data.pubKey ||
      !data.prUrl
    ) {
      console.error("INVALID SIGNATURE DATA");
      return null;
    }
    return data;
}