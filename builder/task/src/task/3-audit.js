import { getFile } from '../helpers.js';
import { getOrcaClient } from '@_koii/task-manager/extensions';

export async function audit(cid, roundNumber) {
  /**
   * Audit a submission
   * This function should return true if the submission is correct, false otherwise
   * The default implementation retrieves the proofs from IPFS
   * and sends them to your container for auditing
   */
  console.log(`AUDIT SUBMISSION FOR ROUND ${roundNumber}`);
  const submission = await getFile(cid);
  console.log({ submission });
  const orca = await getOrcaClient();
  const result = await orca.podCall(`audit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ submission }),
  });
  return result.data;
}
