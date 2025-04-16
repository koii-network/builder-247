import { Router, RequestHandler } from 'express';
import { fetchRequest as fetchSummarizerRequest } from '../controllers/summarizer/fetchRequest';
import { addRequest as addSummarizerRequest } from '../controllers/summarizer/addRequest';
import { triggerFetchAuditResult as triggerFetchAuditResultSummarizer } from '../controllers/summarizer/triggerFetchAuditResult';
import { checkRequest as checkSummarizerRequest } from '../controllers/summarizer/checkRequest';

const router = Router();

// router.post("/fetch-summarizer-todo", fetchSummarizerRequest as RequestHandler);
router.post('/add-pr-to-summarizer-todo', addSummarizerRequest as RequestHandler);
router.post('/trigger-fetch-audit-result', triggerFetchAuditResultSummarizer as RequestHandler);
router.post('/check-summarizer', checkSummarizerRequest as RequestHandler);
// router.post("/trigger-update-swarms-status", triggerUpdateSwarmsStatus as RequestHandler);
// router.post("/trigger-save-swarms-for-round", triggerSaveSwarmsForRound as RequestHandler);

export default router;
