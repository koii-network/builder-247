"""Audit service module."""

import logging
from prometheus_swarm.clients import setup_client
from src.workflows.audit.workflow import AuditWorkflow
from src.workflows.audit.prompts import PROMPTS as AUDIT_PROMPTS

logger = logging.getLogger(__name__)


def audit_issues_and_tasks(issuesAndTasks, issueSpec, repo_owner, repo_name):
    """Review PR and decide if it should be accepted, revised, or rejected."""
    try:
        # Set up client and workflow
        client = setup_client("anthropic")
        workflow = AuditWorkflow(
                client=client,
                prompts=AUDIT_PROMPTS,
                issuesAndTasks=issuesAndTasks,
                issueSpec=issueSpec,
                repo_owner=repo_owner,
                repo_name=repo_name,
        )

        # Run workflow and get result
        result = workflow.run()
        return result
    except Exception as e:
        logger.error(f"PR review failed: {str(e)}")
        raise Exception("PR review failed")
