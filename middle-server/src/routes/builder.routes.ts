import { Router, RequestHandler } from 'express';
import { fetchTodo } from '../controllers/builder/fetchToDo';
import { addPR } from '../controllers/builder/addTodoPR';
import { checkToDo } from '../controllers/builder/checkToDo';
import { updateAuditResult } from '../controllers/builder/updateAuditResult';
import { addAggregatorInfo } from '../controllers/builder/addAggregatorInfo';
import { addIssuePR } from '../controllers/builder/addIssuePR';
import { assignIssue } from '../controllers/builder/assignIssue';
import { fetchIssue } from '../controllers/builder/fetchIssue';
import { checkIssue } from '../controllers/builder/checkIssue';
import { getSourceRepo } from '../controllers/builder/getSourceRepo';
import { recordTaskFailure } from '../controllers/builder/recordTaskFailure';
import { recordAuditFailure } from '../controllers/builder/recordAuditFailure';

const router = Router();

router.post('/fetch-to-do', fetchTodo as RequestHandler);
router.post('/add-aggregator-info', addAggregatorInfo as RequestHandler);
router.post('/add-pr-to-to-do', addPR as RequestHandler);
router.post('/add-issue-pr', addIssuePR as RequestHandler);
router.post('/check-to-do', checkToDo as RequestHandler);
router.post('/assign-issue', assignIssue as RequestHandler);
router.post('/update-audit-result', updateAuditResult as RequestHandler);
router.post('/fetch-issue', fetchIssue as RequestHandler);
router.post('/check-issue', checkIssue as RequestHandler);
router.get('/get-source-repo/:nodeType/:uuid', getSourceRepo as RequestHandler);
router.post('/record-task-failure', recordTaskFailure as RequestHandler);
router.post('/record-audit-failure', recordAuditFailure as RequestHandler);

export default router;
