"""Task workflow phases implementation."""

from src.workflows.base import WorkflowPhase, Workflow


class BranchCreationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow):
        super().__init__(
            workflow=workflow,
            prompt_name="create_branch",
            required_tool="create_branch",
            name="Branch Creation",
        )


class ImplementationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="execute_todo",
            conversation_id=conversation_id,
            name="Implementation",
        )


class ValidationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow):
        super().__init__(
            workflow=workflow,
            prompt_name="validate_criteria",
            available_tools=[
                "read_file",
                "run_tests",
                "validate_implementation",
                "list_files",
            ],
            name="Validation",
        )


class FixImplementationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="fix_implementation",
            conversation_id=conversation_id,
            name="Fix Implementation",
        )


class PullRequestPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="create_pr",
            required_tool="create_pull_request",
            conversation_id=conversation_id,
            name="Create Pull Request",
        )
