"""Task decomposition workflow phases implementation."""

from src.workflows.base import WorkflowPhase, Workflow


class CheckReadmeFilePhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="check_readme_file",
            available_tools=["read_file",  "list_files", "review_pull_request"],
            conversation_id=conversation_id,
            name="Check Readme File",
        )

