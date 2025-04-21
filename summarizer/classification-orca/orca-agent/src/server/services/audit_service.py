"""Audit service module."""

import logging
from prometheus_swarm.clients import setup_client
from src.workflows.repoSummarizerAudit.workflow import repoSummarizerAuditWorkflow
from src.workflows.repoSummarizerAudit.prompts import (
    PROMPTS as REPO_SUMMARIZER_AUDIT_PROMPTS,
)

logger = logging.getLogger(__name__)


def audit_repo(pr_url):
    # def review_pr(repo_urls, pr_url, github_username, star_only=True):
    """Review PR and decide if it should be accepted, revised, or rejected."""
    try:
        # Set up client and workflow
        client = setup_client("anthropic")

        # Below commented out because we won't need to distribute starring repo nodes
        # star_repo_workflow = StarRepoAuditWorkflow(
        #     client=client,
        #     prompts=STAR_REPO_AUDIT_PROMPTS,
        #     repo_url=repo_urls[0],
        #     github_username=github_username,
        # )
        # star_repo_workflow.run()

        repo_summerizer_audit_workflow = repoSummarizerAuditWorkflow(
            client=client,
            prompts=REPO_SUMMARIZER_AUDIT_PROMPTS,
            pr_url=pr_url,
        )

        # Run workflow and get result
        result = repo_summerizer_audit_workflow.run()
        recommendation = result["data"]["recommendation"]
        return recommendation
    except Exception as e:
        logger.error(f"PR review failed: {str(e)}")
        raise Exception("PR review failed")


if __name__ == "__main__":
    # review_pr(["https://github.com/alexander-morris/koii-dumper-reveal"], "https://github.com/koii-network/namespace-wrapper/pull/1", "HermanL02")

    audit_repo("https://github.com/koii-network/namespace-wrapper/pull/1")
