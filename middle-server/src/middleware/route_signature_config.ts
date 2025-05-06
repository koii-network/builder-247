// List of routes that require signature validation
export const signatureValidationRoutes = [
  '/builder/fetch-to-do',
  '/builder/add-aggregator-info',
  '/builder/add-pr-to-to-do',
  '/builder/add-issue-pr',
  '/builder/check-to-do',
  '/builder/assign-issue',
  '/builder/update-audit-result',
  '/builder/fetch-issue',
  '/builder/check-issue',
  '/summarizer/fetch-summarizer-todo',
  '/summarizer/add-pr-to-summarizer-todo',
  '/summarizer/trigger-fetch-audit-result',
  '/summarizer/check-summarizer',
  '/planner/fetch-planner-todo',
  '/planner/add-pr-to-planner-todo', 
  '/planner/check-planner',
  '/planner/trigger-fetch-audit-result',
  '/supporter/bind-key-to-github',
  '/supporter/fetch-repo-list',
  '/supporter/check-request'
];