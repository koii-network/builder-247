import { Router } from "express";
import { fetchTodo } from "../controllers/fetchToDo";
import { addPR } from "../controllers/addTodoPR";
import { checkToDo } from "../controllers/checkToDo";
import { triggerFetchAuditResult } from "../controllers/triggerFetchAuditResult";
import type { RequestHandler } from "express";
import { addAggregatorInfo } from "../controllers/addAggregatorInfo";
import { addIssuePR } from "../controllers/addIssuePR";
import { getIssuePrUrls } from "../controllers/getIssuePrUrls";
// import { triggerUpdateSwarmsStatus } from "./controllers/summarizer/triggerUpdateSwarmsStatus";
// import { triggerSaveSwarmsForRound } from "../controllers/summarizer/triggerSaveSwarmsForRound";
import { fetchSummarizerTodo } from "../controllers/summarizer/fetchSummarizer";
import { addPRToSummarizerTodo } from "../controllers/summarizer/addDocsRequest";
import { triggerFetchAuditResult as triggerFetchAuditResultSummarizer } from "../controllers/summarizer/triggerFetchAuditResult";
// import { fetchSummarizerTodo as fetchSummarizerTodoLogic } from "../controllers/summarizer/fetchSummarizer";

import { checkSummarizer } from "../controllers/summarizer/checkSummarizer";
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
router.post("/summarizer/fetch-summarizer-todo", fetchSummarizerTodo as RequestHandler);
router.post("/summarizer/add-pr-to-summarizer-todo", addPRToSummarizerTodo as RequestHandler);
router.post("/summarizer/trigger-fetch-audit-result", triggerFetchAuditResultSummarizer as RequestHandler);
router.post("/summarizer/check-summarizer", checkSummarizer as RequestHandler);
router.get("/hello", (req, res) => {
  res.json({ message: "Hello World!" });
});
export default router;
