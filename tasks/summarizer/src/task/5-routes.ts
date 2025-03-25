import { namespaceWrapper, app } from "@_koii/task-manager/namespace-wrapper";
import { getLeaderNode } from "../utils/leader";
import { task } from "./1-task";
import { submission } from "./2-submission";
import { audit } from "./3-audit";
import { distribution } from "./4-distribution";
/**
 *
 * Define all your custom routes here
 *
 */

//Example route
export async function routes() {
  app.get("/value", async (_req, res) => {
    const value = await namespaceWrapper.storeGet("value");
    console.log("value", value);
    res.status(200).json({ value: value });
  });

  app.get("/leader/:roundNumber/:submitterPublicKey", async (req, res) => {
    const roundNumber = req.params.roundNumber;
    const submitterPublicKey = req.params.submitterPublicKey;
    const {isLeader, leaderNode} = await getLeaderNode({roundNumber: Number(roundNumber), submitterPublicKey: submitterPublicKey});
    res.status(200).json({ isLeader: isLeader, leaderNode: leaderNode });
  });

  app.get("/task/:roundNumber", async (req, res) => {
    console.log("task endpoint called with round number: ", req.params.roundNumber);
    const roundNumber = req.params.roundNumber;
    const taskResult = await task(Number(roundNumber));
    res.status(200).json({ result: taskResult });
  });

  app.get("/submission/:roundNumber", async (req, res) => {
    const roundNumber = req.params.roundNumber;
    const submissionResult = await submission(Number(roundNumber));
    res.status(200).json({ result: submissionResult });
  });

  app.get("/audit/:roundNumber/:cid", async (req, res) => {
    const roundNumber = req.params.roundNumber;
    const cid = req.params.cid;
    const auditResult = await audit(cid, Number(roundNumber), "submitter");
    res.status(200).json({ result: auditResult });
  });

}
