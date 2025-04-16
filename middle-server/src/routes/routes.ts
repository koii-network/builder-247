import { Router, RequestHandler } from "express";

/******** Builder *********/
import { fetchTodo } from "../controllers/builder/fetchToDo";
import { addPR } from "../controllers/builder/addTodoPR";
import { checkToDo } from "../controllers/builder/checkToDo";
import { updateAuditResult } from "../controllers/builder/updateAuditResult";
import { addAggregatorInfo } from "../controllers/builder/addAggregatorInfo";
import { addIssuePR } from "../controllers/builder/addIssuePR";
import { assignIssue } from "../controllers/builder/assignIssue";
import { fetchIssue } from "../controllers/builder/fetchIssue";
import { checkIssue } from "../controllers/builder/checkIssue";
import { getSourceRepo } from "../controllers/builder/getSourceRepo";

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
import { getAssignedTo } from "../controllers/prometheus/getAssignedTo";


/********** Supporter ***********/
import { bindRequest } from "../controllers/supporter/bindRequest";
import { fetchRequest as fetchRepoList } from "../controllers/supporter/fetchRequest";
import { checkRequest as checkRepoRequest } from "../controllers/supporter/checkRequest";

const router = Router();

/********** Builder ***********/
router.post("/builder/fetch-to-do", fetchTodo as RequestHandler);
router.post("/builder/add-aggregator-info", addAggregatorInfo as RequestHandler);
router.post("/builder/add-pr-to-to-do", addPR as RequestHandler);
router.post("/builder/add-issue-pr", addIssuePR as RequestHandler);
router.post("/builder/check-to-do", checkToDo as RequestHandler);
router.post("/builder/assign-issue", assignIssue as RequestHandler);
router.post("/builder/update-audit-result", updateAuditResult as RequestHandler);
router.post("/builder/fetch-issue", fetchIssue as RequestHandler);
router.post("/builder/check-issue", checkIssue as RequestHandler);
router.get("/builder/get-source-repo/:nodeType/:uuid", getSourceRepo as RequestHandler);

/********** Summarizer */
// router.post("/summarizer/fetch-summarizer-todo", fetchSummarizerRequest as RequestHandler);
router.post("/summarizer/add-pr-to-summarizer-todo", addSummarizerRequest as RequestHandler);
router.post("/summarizer/trigger-fetch-audit-result", triggerFetchAuditResultSummarizer as RequestHandler);
router.post("/summarizer/check-summarizer", checkSummarizerRequest as RequestHandler);
// router.post("/summarizer/trigger-update-swarms-status", triggerUpdateSwarmsStatus as RequestHandler);
// router.post("/summarizer/trigger-save-swarms-for-round", triggerSaveSwarmsForRound as RequestHandler);

/********** Planner ***********/
router.post("/planner/fetch-planner-todo", fetchPlannerRequest as RequestHandler);
router.post("/planner/add-pr-to-planner-todo", addPlannerRequest as RequestHandler);
router.post("/planner/check-planner", checkPlannerRequest as RequestHandler);
router.post("/planner/trigger-fetch-audit-result", triggerFetchAuditResultPlanner as RequestHandler);

/*********** Prometheus Website ***********/
router.get("/prometheus/get-assigned-nodes", getAssignedTo as RequestHandler);


/****************** Supporter **************/
router.post("/supporter/bind-key-to-github", bindRequest as RequestHandler);
router.post("/supporter/fetch-repo-list", fetchRepoList as RequestHandler);
router.post("/supporter/check-repo-request", checkRepoRequest as RequestHandler);

router.get("/hello", (req, res) => {
  res.json({ message: "Hello World!" });
});

export default router;
