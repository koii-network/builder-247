import { Router, RequestHandler } from 'express';
import { fetchRequest as fetchPlannerRequest } from '../controllers/planner/fetchRequest';
import { addRequest as addPlannerRequest } from '../controllers/planner/addRequest';
import { checkRequest as checkPlannerRequest } from '../controllers/planner/checkRequest';
import { triggerFetchAuditResult as triggerFetchAuditResultPlanner } from '../controllers/planner/triggerFetchAuditResult';

const router = Router();

router.post('/fetch-planner-todo', fetchPlannerRequest as RequestHandler);
router.post('/add-pr-to-planner-todo', addPlannerRequest as RequestHandler);
router.post('/check-planner', checkPlannerRequest as RequestHandler);
router.post('/trigger-fetch-audit-result', triggerFetchAuditResultPlanner as RequestHandler);

export default router;
