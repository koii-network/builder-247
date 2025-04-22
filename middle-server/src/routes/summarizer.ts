import { Router, RequestHandler } from 'express';
// import { fetchRequest as fetchSummarizerRequest } from '../controllers/summarizer/fetchRequest';
import { addRequest as addSummarizerRequest } from '../controllers/summarizer/addRequest';
import { triggerFetchAuditResult as triggerFetchAuditResultSummarizer } from '../controllers/summarizer/triggerFetchAuditResult';
import { checkRequest as checkSummarizerRequest } from '../controllers/summarizer/checkRequest';

const router = Router();

/********** Worker ***********/
// router.post("/worker/fetch-summarizer-todo", fetchSummarizerRequest as RequestHandler);
router.post('/worker/add-todo-pr', addSummarizerRequest as RequestHandler);
router.post('/worker/update-audit-result', triggerFetchAuditResultSummarizer as RequestHandler);
router.post('/worker/check-todo', checkSummarizerRequest as RequestHandler);
// router.post("/worker/trigger-update-swarms-status", triggerUpdateSwarmsStatus as RequestHandler);
// router.post("/worker/trigger-save-swarms-for-round", triggerSaveSwarmsForRound as RequestHandler);

export default router;
