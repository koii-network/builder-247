import { Router, RequestHandler } from 'express';

import { getAssignedTo } from '../controllers/prometheus/getAssignedTo';

const router = Router();

router.get('/get-assigned-nodes', getAssignedTo as RequestHandler);

export default router;
