"""Audit phase definitions."""

from prometheus_swarm.workflows.base import Workflow, WorkflowPhase


class TaskValidationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="audit_tasks",
            available_tools=[
                "read_file",
                "audit_tasks",
            ],
            conversation_id=conversation_id,
            name="Task Validation",
        )
