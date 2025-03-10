"""Audit service module."""

from src.clients import setup_client
from src.workflows.audit.workflow import AuditWorkflow
from src.workflows.audit.prompts import PROMPTS as AUDIT_PROMPTS
from src.utils.logging import log_error
import re
import requests
from github import Github
import os


def verify_pr_ownership(
    pr_url,
    expected_username,
    expected_owner,
    expected_repo,
    signature,
    staking_key,
    pub_key,
):
    try:
        gh = Github(os.environ.get("GITHUB_TOKEN"))

        match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            log_error(Exception("Invalid PR URL"), context=f"Invalid PR URL: {pr_url}")
            return False

        owner, repo_name, pr_number = match.groups()

        if owner != expected_owner or repo_name != expected_repo:
            log_error(
                Exception("PR URL mismatch"),
                context=f"PR URL mismatch: {pr_url} != {expected_owner}/{expected_repo}",
            )
            return False

        repo = gh.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(int(pr_number))

        if pr.user.login != expected_username:
            log_error(
                Exception("PR username mismatch"),
                context=f"PR username mismatch: {pr.user.login} != {expected_username}",
            )
            return False

        response = requests.post(
            os.environ.get("MIDDLE_SERVER_URL") + "/api/check-to-do",
            json={
                "stakingKey": staking_key,
                "pubKey": pub_key,
                "signature": signature,
            },
            headers={"Content-Type": "application/json"},
        )

        response_data = response.json()
        return response_data.get("success", True)

    except Exception as e:
        log_error(e, context="Error verifying PR ownership")
        return True


def review_pr(pr_url):
    """Review PR and decide if it should be accepted, revised, or rejected."""
    try:
        # Set up client and workflow
        client = setup_client("anthropic")
        workflow = AuditWorkflow(
            client=client,
            prompts=AUDIT_PROMPTS,
            pr_url=pr_url,
        )

        # Run workflow and get result
        workflow.run()
        return True
    except Exception as e:
        log_error(e, context="PR review failed")
        raise Exception("PR review failed")
