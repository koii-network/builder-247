"""Audit phase definitions."""

from typing import List
from src.workflows.base import Workflow, WorkflowPhase, requires_context


@requires_context(
    templates={
        "pr_url": str,  # URL of the PR to review
        "repo_owner": str,  # Owner of the repository
        "repo_name": str,  # Name of the repository
        "pr_number": int,  # PR number to review
        "current_files": List[str],  # Current repository structure
    },
    tools={
        "repo_owner": str,  # Owner of the repository
        "repo_name": str,  # Name of the repository
        "pr_number": int,  # PR number to review
        "repo_path": str,  # Path to the repository
    },
)
class AuditPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow):
        super().__init__(
            workflow=workflow,
            prompt_name="review_pr",
            available_tools=[
                "read_file",
                "list_files",
                "run_tests",
                "review_pull_request",
            ],
            name="PR Review",
        )
