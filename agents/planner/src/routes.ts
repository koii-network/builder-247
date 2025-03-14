import { Router } from "express";
import { fetchTodo } from "./controllers/fetchToDo";
import { addPR } from "./controllers/addTodoPR";
import { checkToDo } from "./controllers/checkToDo";
import { triggerFetchAuditResult } from "./controllers/triggerFetchAuditResult";
import type { RequestHandler } from "express";
import { addAggregatorInfo } from "./controllers/addAggregatorInfo";
import { addIssuePR } from "./controllers/addIssuePR";

const router = Router();

router.post("/fetch-to-do", fetchTodo as RequestHandler);
router.post("/add-aggregator-info", addAggregatorInfo as RequestHandler);
router.post("/add-pr-to-to-do", addPR as RequestHandler);
router.post("/add-issue-pr", addIssuePR as RequestHandler);
router.post("/check-to-do", checkToDo as RequestHandler);
router.post("/trigger-fetch-audit-result", triggerFetchAuditResult as RequestHandler);

export default router;
