import { Router, RequestHandler } from "express";
import { verifyBearerToken } from "../middleware/auth";
import { validateSignature } from "../middleware/signatureValidation";

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

/******** Prometheus Website ***********/
import { getAssignedTo } from "../controllers/prometheus/getAssignedTo";
import { classification } from "../controllers/prometheus/classification";

/********** Supporter ***********/
import { bindRequest } from "../controllers/supporter/bindRequest";
import { fetchRequest as fetchRepoList } from "../controllers/supporter/fetchRequest";
import { checkRequest as checkRepoRequest } from "../controllers/supporter/checkRequest";
import { info } from "../controllers/prometheus/info";

const router = Router();

/********** Builder ***********/
router.post("/builder/fetch-to-do", validateSignature, fetchTodo as RequestHandler);
router.post("/builder/add-aggregator-info", validateSignature, addAggregatorInfo as RequestHandler);
router.post("/builder/add-pr-to-to-do", validateSignature, addPR as RequestHandler);
router.post("/builder/add-issue-pr", validateSignature, addIssuePR as RequestHandler);
router.post("/builder/check-to-do", validateSignature, checkToDo as RequestHandler);
router.post("/builder/assign-issue", validateSignature, assignIssue as RequestHandler);
router.post("/builder/update-audit-result", validateSignature, updateAuditResult as RequestHandler);
router.post("/builder/fetch-issue", validateSignature, fetchIssue as RequestHandler);
router.post("/builder/check-issue", validateSignature, checkIssue as RequestHandler);
router.get("/builder/get-source-repo/:nodeType/:uuid", validateSignature, getSourceRepo as RequestHandler);

/********** Summarizer */
router.post("/summarizer/fetch-summarizer-todo", validateSignature, fetchSummarizerRequest as RequestHandler);
router.post("/summarizer/add-pr-to-summarizer-todo", validateSignature, addSummarizerRequest as RequestHandler);
router.post("/summarizer/trigger-fetch-audit-result", validateSignature, triggerFetchAuditResultSummarizer as RequestHandler);
router.post("/summarizer/check-summarizer", validateSignature, checkSummarizerRequest as RequestHandler);

/********** Planner ***********/
router.post("/planner/fetch-planner-todo", validateSignature, fetchPlannerRequest as RequestHandler);
router.post("/planner/add-pr-to-planner-todo", validateSignature, addPlannerRequest as RequestHandler);
router.post("/planner/check-planner", validateSignature, checkPlannerRequest as RequestHandler);
router.post("/planner/trigger-fetch-audit-result", validateSignature, triggerFetchAuditResultPlanner as RequestHandler);

/*********** Prometheus Website ***********/
router.get("/prometheus/get-assigned-nodes", validateSignature, getAssignedTo as RequestHandler);
router.post("/prometheus/classification", verifyBearerToken, validateSignature, classification as RequestHandler);
router.get("/prometheus/info", validateSignature, info as RequestHandler);

/****************** Supporter **************/
router.post("/supporter/bind-key-to-github", validateSignature, bindRequest as RequestHandler);
router.post("/supporter/fetch-repo-list", validateSignature, fetchRepoList as RequestHandler);
router.post("/supporter/check-request", validateSignature, checkRepoRequest as RequestHandler);

router.get("/hello", (req, res) => {
  res.json({ message: "Hello World!" });
});

export default router;