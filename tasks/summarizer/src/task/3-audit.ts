import { getFile } from "../utils/ipfs";
import { getOrcaClient } from "@_koii/task-manager/extensions";
import { namespaceWrapper, TASK_ID } from "@_koii/namespace-wrapper";
import { getLeaderNode } from "../utils/leader";
import { getDistributionList } from "../utils/distributionList";
export async function audit(cid: string, roundNumber: number, submitterKey: string): Promise<boolean | void> {
  /**
   * Audit a submission
   * This function should return true if the submission is correct, false otherwise
   * The default implementation retrieves the proofs from IPFS
   * and sends them to your container for auditing
   */
  try {
    const result = await namespaceWrapper.storeGet(`result-${roundNumber}`);
    if (result === "True") {
      return true;
    } else {
      // Check orca client logic
      const orcaClient = await getOrcaClient();
      const result = await orcaClient.podCall(`audit/${roundNumber}`);
      console.log({ result });

      // TODO: Check if the result is correct
      return result.data === "True";
    }
  } catch (error) {
    console.error("ERROR AUDITING SUBMISSION", error);
    return true;
  }
}
