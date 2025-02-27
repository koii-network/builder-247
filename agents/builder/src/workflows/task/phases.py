"""Task workflow phases implementation."""

from src.workflows.base import WorkflowPhase


class BranchCreationPhase(WorkflowPhase):
    def __init__(self):
        super().__init__(
            prompt_name="create_branch",
            required_tool="create_branch",
            name="Branch Creation",
        )


class ImplementationPhase(WorkflowPhase):
    def __init__(self, conversation_id: str):
        super().__init__(
            prompt_name="execute_todo",
            conversation_id=conversation_id,
            name="Implementation",
        )


class ValidationPhase(WorkflowPhase):
    def __init__(self):
        super().__init__(
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
    def __init__(self, conversation_id: str):
        super().__init__(
            prompt_name="fix_implementation",
            conversation_id=conversation_id,
            name="Fix Implementation",
        )


class PullRequestPhase(WorkflowPhase):
    def __init__(self, conversation_id: str):
        super().__init__(
            prompt_name="create_pr",
            required_tool="create_pr",
            conversation_id=conversation_id,
            name="Create Pull Request",
        )
