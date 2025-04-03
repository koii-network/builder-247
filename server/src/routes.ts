import { Router } from "express";
import { fetchTodo } from "./controllers/fetchToDo";
import { addPR } from "./controllers/addTodoPR";
import { checkToDo } from "./controllers/checkToDo";
import { updateAuditResult } from "./controllers/updateAuditResult";
import type { RequestHandler } from "express";
import { addAggregatorInfo } from "./controllers/addAggregatorInfo";
import { addIssuePR } from "./controllers/addIssuePR";
// import { getIssuePrUrls } from "./controllers/getIssuePrUrls";
import { assignIssue } from "./controllers/assignIssue";
import { fetchIssue } from "./controllers/fetchIssue";

const router = Router();

router.post("/fetch-to-do", fetchTodo as RequestHandler);
router.post("/add-aggregator-info", addAggregatorInfo as RequestHandler);
router.post("/add-pr-to-to-do", addPR as RequestHandler);
router.post("/add-issue-pr", addIssuePR as RequestHandler);
router.post("/check-to-do", checkToDo as RequestHandler);
router.post("/assign-issue", assignIssue as RequestHandler);
router.post("/update-audit-result", updateAuditResult as RequestHandler);
// router.get("/get-issue-pr-urls/:issueUuid", getIssuePrUrls as RequestHandler);
router.post("/fetch-issue", fetchIssue as RequestHandler);

export default router;
