"""Task workflow phases."""

from typing import List
from prometheus_swarm.workflows.base import WorkflowPhase, Workflow, requires_context


@requires_context(
    templates={
        "current_files": List[str],  # List of files in the repository
        "repo_path": str,  # Path to the repository
        "repo_owner": str,  # Leader's username
        "repo_name": str,  # Repository name
        "todo": str,  # Todo task description
        "acceptance_criteria": List[str],  # List of acceptance criteria
        "base_branch": str,  # Base branch to target
        "github_token": str,  # GitHub token for authentication
    },
    tools={
        "repo_path": str,  # Path to the repository for git operations
        "repo_owner": str,  # Leader's username for PR target
        "repo_name": str,  # Repository name for PR target
        "base_branch": str,  # Base branch for PR target
        "github_token": str,  # GitHub token for authentication
    },
)
class BranchCreationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="create_branch",
            available_tools=["create_branch"],
            conversation_id=conversation_id,
            name="Branch Creation",
        )


@requires_context(
    templates={
        "current_files": List[str],  # List of files in the repository
        "repo_path": str,  # Path to the repository
        "todo": str,  # Todo task description
        "acceptance_criteria": List[str],  # List of acceptance criteria
    },
    tools={
        "repo_path": str,  # Path to the repository for git operations
    },
)
class ImplementationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="implement_todo",
            available_tools=[
                "read_file",
                "list_files",
                "write_file",
                "delete_file",
                "run_tests",
                "install_dependency",
                "setup_dependencies",
                "create_directory",
            ],
            conversation_id=conversation_id,
            name="Implementation",
        )


@requires_context(
    templates={
        "current_files": List[str],  # List of files in the repository
        "repo_path": str,  # Path to the repository
        "todo": str,  # Todo task description
        "acceptance_criteria": List[str],  # List of acceptance criteria
        "previous_issues": str,  # Issues from previous validation
    },
    tools={
        "repo_path": str,  # Path to the repository for git operations
    },
)
class FixImplementationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="fix_implementation",
            available_tools=[
                "read_file",
                "list_files",
                "edit_file",
                "delete_file",
                "run_tests",
                "install_dependency",
            ],
            conversation_id=conversation_id,
            name="Fix Implementation",
        )


@requires_context(
    templates={
        "current_files": List[str],  # List of files in the repository
        "repo_path": str,  # Path to the repository
        "todo": str,  # Todo task description
        "acceptance_criteria": List[str],  # List of acceptance criteria
    },
    tools={
        "repo_path": str,  # Path to the repository for git operations
    },
)
class ValidationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="validate_criteria",
            available_tools=[
                "read_file",
                "list_files",
                "run_tests",
                "validate_implementation",
            ],
            conversation_id=conversation_id,
            name="Validation",
        )


@requires_context(
    templates={
        "current_files": List[str],  # List of files in the repository
        "repo_path": str,  # Path to the repository
        "repo_owner": str,  # Leader's username for PR target
        "repo_name": str,  # Repository name for PR target
        "todo": str,  # Todo task description
        "acceptance_criteria": List[str],  # List of acceptance criteria
        "base_branch": str,  # Base branch for PR target
        "staking_key": str,  # Worker's staking key
        "pub_key": str,  # Worker's public key
        "staking_signature": str,  # Worker's staking signature
        "public_signature": str,  # Worker's public signature
    },
    tools={
        "repo_path": str,  # Path to the repository for git operations
        "repo_owner": str,  # Leader's username for PR target
        "repo_name": str,  # Repository name for PR target
        "base_branch": str,  # Base branch for PR target
        "staking_key": str,  # Worker's staking key
        "pub_key": str,  # Worker's public key
        "staking_signature": str,  # Worker's staking signature
        "public_signature": str,  # Worker's public signature
        "github_token": str,  # GitHub token for authentication
    },
)
class PullRequestPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="create_pr",
            available_tools=["read_file", "list_files", "create_worker_pull_request"],
            conversation_id=conversation_id,
            name="Create Pull Request",
        )
