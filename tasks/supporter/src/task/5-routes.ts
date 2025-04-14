import { namespaceWrapper, app } from "@_koii/task-manager/namespace-wrapper";
import { getLeaderNode, getRandomNodes } from "../utils/leader";
import { task } from "./1-task";
import { submission } from "./2-submission";
import { audit } from "./3-audit";
import { distribution } from "./4-distribution";
import { submissionJSONSignatureDecode } from "../utils/submissionJSONSignatureDecode";
import { Submission } from "@_koii/namespace-wrapper/dist/types";
import { taskRunner } from "@_koii/task-manager"

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
  app.get("/audit/:roundNumber/:cid/:submitterPublicKey", async (req, res) => {
    const cid = req.params.cid;
    const roundNumber = req.params.roundNumber;
    const submitterPublicKey = req.params.submitterPublicKey;
    const auditResult = await audit(cid, Number(roundNumber), submitterPublicKey);
    res.status(200).json({ result: auditResult });
  });
  app.get("/submission/:roundNumber", async (req, res) => {
    const roundNumber = req.params.roundNumber;
    const submissionResult = await submission(Number(roundNumber));
    res.status(200).json({ result: submissionResult });
  });

  app.get("/submitDistribution/:roundNumber", async (req, res) => {
    const roundNumber = req.params.roundNumber;
    const submitDistributionResult = await taskRunner.submitDistributionList(Number(roundNumber));
    res.status(200).json({ result: submitDistributionResult });
  });

}
