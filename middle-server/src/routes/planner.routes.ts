import { Router, RequestHandler } from 'express';
import { fetchRequest } from '../controllers/planner/fetchRequest';
import { addRequest } from '../controllers/planner/addRequest';
import { checkRequest } from '../controllers/planner/checkRequest';
import { triggerFetchAuditResult } from '../controllers/planner/triggerFetchAuditResult';

const router = Router();

router.post('/fetch-planner-todo', fetchRequest as RequestHandler);
router.post('/add-pr-to-planner-todo', addRequest as RequestHandler);
router.post('/check-planner', checkRequest as RequestHandler);
router.post('/trigger-fetch-audit-result', triggerFetchAuditResult as RequestHandler);

export default router;
