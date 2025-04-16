import { Router, RequestHandler } from 'express';

import { bindRequest } from '../controllers/supporter/bindRequest';
import { fetchRequest as fetchRepoList } from '../controllers/supporter/fetchRequest';
import { checkRequest as checkRepoRequest } from '../controllers/supporter/checkRequest';

const router = Router();

router.post('/bind-key-to-github', bindRequest as RequestHandler);
router.post('/fetch-repo-list', fetchRepoList as RequestHandler);
router.post('/check-repo-request', checkRepoRequest as RequestHandler);

export default router;
