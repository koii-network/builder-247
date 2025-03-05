"""Bug finder workflow phases implementation."""

from src.workflows.base import WorkflowPhase, Workflow


class CodeAnalysisPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="analyze_code",
            available_tools=[
                "read_file",
                "list_files",
                "generate_analysis",
            ],
            conversation_id=conversation_id,
            name="Code Analysis",
        )
