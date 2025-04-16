import express from 'express';
import mongoose from 'mongoose';
import http from 'http';
import morgan from 'morgan';
import { checkConnections } from './services/database/database';

// Import route files
import builderRoutes from './routes/builder.routes';
import plannerRoutes from './routes/planner.routes';
import summarizerRoutes from './routes/summarizer.routes';

export const app = express();
const port = process.env.PORT || 3000;

// Define custom morgan token for colored status
morgan.token('status-colored', (req, res) => {
  const status = res.statusCode;
  const color =
    status >= 500
      ? 31 // red
      : status >= 400
        ? 33 // yellow
        : status >= 300
          ? 36 // cyan
          : 32; // green
  return `\x1b[${color}m${status}\x1b[0m`;
});

// Add this middleware before morgan to capture response body
app.use((req, res, next) => {
  const originalJson = res.json;
  res.json = function (body) {
    res.locals.responseBody = body;
    return originalJson.call(this, body);
  };
  next();
});

// Add custom token for error message
morgan.token('error-message', (req, res) => {
  const expressRes = res as express.Response;
  if (expressRes.statusCode >= 400) {
    return expressRes.locals.responseBody?.message || '';
  }
  return '';
});

// Modified morgan configuration
app.use(
  morgan(':method :url :status-colored :error-message - :response-time ms', {
    skip: (req) => req.url === '/healthz',
  })
);

// Add body-parser middleware
app.use(express.json());

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('\x1b[31m%s\x1b[0m', 'Error:', {
    timestamp: new Date().toISOString(),
    name: err.name,
    message: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    body: req.body,
    query: req.query,
    headers: req.headers,
  });

  res.status(500).json({
    success: false,
    message: 'Internal server error',
  });
});

app.get('/', (req: express.Request, res: express.Response) => {
  res.send('Hello World!');
});

// Use separate route files
app.use('/api/builder', builderRoutes);
app.use('/api/planner', plannerRoutes);
app.use('/api/summarizer', summarizerRoutes);

export async function connectToDatabase() {
  try {
    await checkConnections();
    console.log('\x1b[32m%s\x1b[0m', 'Connected to MongoDB');
  } catch (error) {
    console.error('\x1b[31m%s\x1b[0m', 'Error connecting to MongoDB:', error);
  }
}

export function startServer(): http.Server {
  return app.listen(port, () => {
    console.log('\x1b[36m%s\x1b[0m', `Server running at http://localhost:${port}`);
  });
}

export default app;
