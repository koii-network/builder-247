import { namespaceWrapper, app } from "@_koii/task-manager/namespace-wrapper";
import { getLeaderNode } from "../utils/leader";
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

  app.get("/leader/:roundNumber", async (req, res) => {
    const roundNumber = req.params.roundNumber;
    const leader = await getLeaderNode(Number(roundNumber));
    res.status(200).json({ leader: leader });
  });
}
