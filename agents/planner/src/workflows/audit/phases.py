"""Audit phase definitions."""

from src.workflows.base import Workflow, WorkflowPhase


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
