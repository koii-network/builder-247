"""Task decomposition workflow phases implementation."""

from prometheus_swarm.workflows.base import WorkflowPhase, Workflow


class IssueGenerationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="generate_issues",
            available_tools=["generate_issues"],
            conversation_id=conversation_id,
            name="Issue Generation",
        )

class TaskDecompositionPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="decompose_feature",
            available_tools=[
                "read_file",
                "list_files",
                "generate_tasks",
            ],
            conversation_id=conversation_id,
            name="Task Decomposition",
        )


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

class TaskRegenerationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="regenerate_subtasks",
            available_tools=[
                "read_file",
                "regenerate_tasks",
            ],
            conversation_id=conversation_id,
            name="Task Regeneration",
        )

# TODO: Implement Task Dependency Phase
class TaskDependencyPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow,  conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="dependency_tasks",
            available_tools=[
                "read_file",
                "create_task_dependency",
            ],
            conversation_id=conversation_id,
            name="Task Dependency",
        )