import { TASK_ID } from "@_koii/namespace-wrapper";
import { getFile } from "./ipfs";
import { Submission } from "@_koii/namespace-wrapper/dist/types";
import { Submitter } from "@_koii/task-manager/dist/types/global";
import { namespaceWrapper } from "@_koii/namespace-wrapper";
export async function submissionJSONSignatureDecode({submitterSubmission, submitter, roundNumber}: {submitterSubmission: Submission, submitter: Submitter, roundNumber: number}) {
    const submissionString = await getFile(submitterSubmission.submission_value);
    const submission = JSON.parse(submissionString);
    // verify the signature of the submission
    
    const signaturePayload = await namespaceWrapper.verifySignature(submission.signature, submitter.publicKey);
    if (!signaturePayload.data) {
      console.error("INVALID SIGNATURE");
      return null;
    }
    const data = JSON.parse(signaturePayload.data);

    if (
      data.taskId !== TASK_ID ||
      data.roundNumber !== roundNumber ||
      data.stakingKey !== submitter.publicKey ||
      !data.pubKey ||
      !data.prUrl
    ) {
      console.error("INVALID SIGNATURE DATA");
      return null;
    }
}