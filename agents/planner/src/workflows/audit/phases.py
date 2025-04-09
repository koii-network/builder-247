"""Audit phase definitions."""

from src.workflows.base import Workflow, WorkflowPhase


class TaskValidationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="validate_subtasks",
            available_tools=[
                "read_file",
                "validate_tasks",
            ],
            conversation_id=conversation_id,
            name="Task Validation",
        )
