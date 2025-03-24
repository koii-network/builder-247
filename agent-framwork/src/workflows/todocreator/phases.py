"""Task decomposition workflow phases implementation."""

from typing import List, Dict
from src.workflows.base import WorkflowPhase, Workflow, requires_context


class IssueGenerationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="generate_issues",
            available_tools=["generate_issues"],
            conversation_id=conversation_id,
            name="Issue Generation",
        )


@requires_context(
    templates={
        "feature_spec": str,  # Feature specification to decompose
        "repo_url": str,  # URL of the repository
        "output_csv_path": str,  # Path to output CSV file
        "current_files": List[str],  # Current repository structure
    },
    tools={
        "repo_path": str,  # Path to the repository
        "output_csv_path": str,  # Path for task output
    },
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


@requires_context(
    templates={
        "subtasks": List[Dict[str, any]],  # List of generated subtasks to validate
    },
    tools={
        "output_csv_path": str,  # Path to the tasks CSV file
    },
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
    def __init__(self, workflow: Workflow, conversation_id: str = None):
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
