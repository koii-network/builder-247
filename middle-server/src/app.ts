import express, { Application } from 'express';
import { json } from 'body-parser';
import cors from 'cors';
import router from './routes/routes';
import { validateSignature } from './middleware/signature_validation';
import { signatureValidationRoutes } from './middleware/route_signature_config';

const app: Application = express();

// Middleware
app.use(cors());
app.use(json());

// Apply signature validation middleware to specific routes
app.use((req, res, next) => {
  const path = req.path;
  if (signatureValidationRoutes.includes(path)) {
    validateSignature(req, res, next);
  } else {
    next();
  }
});

// Routes
app.use('/', router);

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

export default app;