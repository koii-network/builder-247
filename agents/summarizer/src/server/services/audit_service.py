"""Audit service module."""

import logging
from src.clients import setup_client
from src.workflows.starRepoAudit.workflow import StarRepoAuditWorkflow
from src.workflows.starRepoAudit.prompts import PROMPTS as STAR_REPO_AUDIT_PROMPTS
from src.workflows.repoSummerizerAudit.workflow import RepoSummerizerAuditWorkflow
from src.workflows.repoSummerizerAudit.prompts import PROMPTS as REPO_SUMMARIZER_AUDIT_PROMPTS

logger = logging.getLogger(__name__)


def review_pr(repo_urls, pr_url, github_username):
    """Review PR and decide if it should be accepted, revised, or rejected."""
    try:
        # Set up client and workflow
        client = setup_client("anthropic")
        star_repo_workflow = StarRepoAuditWorkflow(
            client=client,
            prompts=STAR_REPO_AUDIT_PROMPTS,
            repo_url=repo_urls[0],
            github_username=github_username,
        )
        star_repo_workflow.run()

        repo_summerizer_audit_workflow = RepoSummerizerAuditWorkflow(
            client=client,
            prompts=REPO_SUMMARIZER_AUDIT_PROMPTS,
            pr_url=pr_url,
        )

        # Run workflow and get result
        repo_summerizer_audit_workflow.run()
        return True
    except Exception as e:
        logger.error(f"PR review failed: {str(e)}")
        raise Exception("PR review failed")
if __name__ == "__main__":
    review_pr(["https://github.com/alexander-morris/koii-dumper-reveal"], "https://github.com/koii-network/namespace-wrapper/pull/1", "HermanL02")