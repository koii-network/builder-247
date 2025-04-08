import { Router } from "express";
import { fetchTodo } from "../controllers/fetchToDo";
import { addPR } from "../controllers/addTodoPR";
import { checkToDo } from "../controllers/checkToDo";
import { triggerFetchAuditResult } from "../controllers/triggerFetchAuditResult";
import type { RequestHandler } from "express";
import { addAggregatorInfo } from "../controllers/addAggregatorInfo";
import { addIssuePR } from "../controllers/addIssuePR";
import { getIssuePrUrls } from "../controllers/getIssuePrUrls";

/******** Summarizer *********/
import { fetchRequest as fetchSummarizerRequest } from "../controllers/summarizer/fetchRequest";
import { addRequest as addSummarizerRequest } from "../controllers/summarizer/addRequest";
import { triggerFetchAuditResult as triggerFetchAuditResultSummarizer } from "../controllers/summarizer/triggerFetchAuditResult";
import { checkRequest as checkSummarizerRequest } from "../controllers/summarizer/checkRequest";

/******** Planner ***********/
import { fetchRequest as fetchPlannerRequest } from "../controllers/planner/fetchRequest";
import { addRequest as addPlannerRequest } from "../controllers/planner/addRequest";
import { checkRequest as checkPlannerRequest } from "../controllers/planner/checkRequest";
import { triggerFetchAuditResult as triggerFetchAuditResultPlanner } from "../controllers/planner/triggerFetchAuditResult";
const router = Router();

router.post("/fetch-to-do", fetchTodo as RequestHandler);
router.post("/add-aggregator-info", addAggregatorInfo as RequestHandler);
router.post("/add-pr-to-to-do", addPR as RequestHandler);
router.post("/add-issue-pr", addIssuePR as RequestHandler);
router.post("/check-to-do", checkToDo as RequestHandler);
router.post("/trigger-fetch-audit-result", triggerFetchAuditResult as RequestHandler);
router.get("/get-issue-pr-urls/:issueUuid", getIssuePrUrls as RequestHandler);
// router.post("/summarizer/trigger-update-swarms-status", triggerUpdateSwarmsStatus as RequestHandler);
// router.post("/summarizer/trigger-save-swarms-for-round", triggerSaveSwarmsForRound as RequestHandler);
/********** Summarizer */
router.post("/summarizer/fetch-summarizer-todo", fetchSummarizerRequest as RequestHandler);
router.post("/summarizer/add-pr-to-summarizer-todo", addSummarizerRequest as RequestHandler);
router.post("/summarizer/trigger-fetch-audit-result", triggerFetchAuditResultSummarizer as RequestHandler);
router.post("/summarizer/check-summarizer", checkSummarizerRequest as RequestHandler);

/********** Planner ***********/
router.post("/planner/fetch-planner-todo", fetchPlannerRequest as RequestHandler);
router.post("/planner/add-pr-to-planner-todo", addPlannerRequest as RequestHandler);
router.post("/planner/check-planner", checkPlannerRequest as RequestHandler);
router.post("/planner/trigger-fetch-audit-result", triggerFetchAuditResultPlanner as RequestHandler);

router.get("/hello", (req, res) => {
  res.json({ message: "Hello World!" });
});
export default router;
