"""Task decomposition workflow phases implementation."""

from src.workflows.base import WorkflowPhase, Workflow


class ReadmeGenerationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="generate_readme_file",
            available_tools=["read_file", "write_file", "list_files", "commit_and_push"],
            conversation_id=conversation_id,
            name="Readme Generation",
        )

