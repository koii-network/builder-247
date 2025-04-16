import { Router, RequestHandler } from 'express';
import { fetchSummarizerTodo } from '../controllers/summarizer/fetchSummarizerTodo';
import { addSummarizerRequest } from '../controllers/summarizer/addSummarizerRequest';
import { checkSummarizer } from '../controllers/summarizer/checkSummarizer';
import { triggerSummarizerAuditResult } from '../controllers/summarizer/triggerSummarizerAuditResult';

const router = Router();

router.post('/fetch-summarizer-todo', fetchSummarizerTodo as RequestHandler);
router.post('/add-pr-to-summarizer-todo', addSummarizerRequest as RequestHandler);
router.post('/check-summarizer', checkSummarizer as RequestHandler);
router.post('/trigger-summarizer-audit-result', triggerSummarizerAuditResult as RequestHandler);

export default router;
