"""Merge conflict resolver workflow phases implementation."""

from src.workflows.base import WorkflowPhase, Workflow


class ConflictResolutionPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="resolve_conflicts",
            available_tools=[
                "read_file",
                "list_files",
                "run_command",
                "resolve_conflict",
                "create_merge_commit",
            ],
            conversation_id=conversation_id,
            name="Conflict Resolution",
        )


class CreatePullRequestPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="create_pr",
            available_tools=[
                "read_file",
                "list_files",
                "run_command",
                "create_pull_request",
            ],
            conversation_id=conversation_id,
            name="Create Pull Request",
        )
