"""Task workflow phases implementation."""

from typing import List, Optional
from src.workflows.base import WorkflowPhase, Workflow, requires_context


@requires_context(
    templates={
        "repo_owner": str,  # Owner of the repository
        "repo_name": str,  # Name of the repository
        "round_number": int,  # Round number for branch naming
        "task_id": str,  # Task ID for branch naming
    },
    tools={
        "repo_owner": str,  # Owner of the repository
        "repo_name": str,  # Name of the repository
    },
)
class BranchCreationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow):
        super().__init__(
            workflow=workflow,
            prompt_name="create_branch",
            required_tool="create_branch",
            name="Branch Creation",
        )


@requires_context(
    templates={
        "todo": str,  # Todo task description
        "acceptance_criteria": List[str],  # Task acceptance criteria
        "repo_path": str,  # Path to the repository
        "current_files": List[str],  # Current repository structure
    },
    tools={
        "repo_path": str,  # Path to the repository
        "current_files": List[str],  # Current repository structure
    },
)
class ImplementationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="execute_todo",
            conversation_id=conversation_id,
            name="Implementation",
        )


@requires_context(
    templates={
        "todo": str,  # Original todo task
        "acceptance_criteria": List[str],  # Task acceptance criteria
        "repo_path": str,  # Path to the repository
        "current_files": List[str],  # Current repository structure
    },
    tools={
        "repo_path": str,  # Path to the repository
        "current_files": List[str],  # Current repository structure
    },
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


@requires_context(
    templates={
        "todo": str,  # Original todo task
        "acceptance_criteria": List[str],  # Task acceptance criteria
        "repo_path": str,  # Path to the repository
        "current_files": List[str],  # Current repository structure
        "validation_issues": List[str],  # Issues found during validation
    },
    tools={
        "repo_path": str,  # Path to the repository
        "current_files": List[str],  # Current repository structure
    },
)
class FixImplementationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="fix_implementation",
            conversation_id=conversation_id,
            name="Fix Implementation",
        )


@requires_context(
    templates={
        "todo": str,  # Original todo task
        "acceptance_criteria": List[str],  # Task acceptance criteria
        "repo_owner": str,  # Owner of the repository
        "repo_name": str,  # Name of the repository
        "branch_name": str,  # Branch name for PR
        "staking_key": Optional[str],  # Worker's staking key
        "pub_key": Optional[str],  # Worker's public key
        "staking_signature": Optional[str],  # Worker's staking signature
        "public_signature": Optional[str],  # Worker's public signature
    },
    tools={
        "repo_owner": str,  # Owner of the repository
        "repo_name": str,  # Name of the repository
        "branch_name": str,  # Branch name for PR
        "staking_key": Optional[str],  # Worker's staking key
        "pub_key": Optional[str],  # Worker's public key
        "staking_signature": Optional[str],  # Worker's staking signature
        "public_signature": Optional[str],  # Worker's public signature
    },
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
