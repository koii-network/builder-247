"""Merge conflict resolver workflow phases."""

from typing import Dict, List
from src.workflows.base import WorkflowPhase, Workflow, requires_context


@requires_context(
    templates={
        "current_files": List[str],  # List of files in the repository
        "repo_path": str,  # Path to the repository
        "current_pr": Dict[
            str, str
        ],  # Current PR info (number, url, repo_owner, repo_name)
    },
    tools={
        "repo_path": str,  # Path to the repository for git operations
        "current_pr": Dict[str, str],  # PR info for conflict resolution
    },
)
class ConflictResolutionPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="resolve_conflicts",
            available_tools=[
                "read_file",
                "list_files",
                "resolve_conflict",
            ],
            conversation_id=conversation_id,
            name="Conflict Resolution",
        )


# @requires_context(
#     templates={
#         "source_fork": Dict[str, str],  # Source fork info (url, owner, name, branch)
#         "working_fork": Dict[str, str],  # Working fork info (url, owner, name)
#         "upstream": Dict[
#             str, str
#         ],  # Upstream repo info (url, owner, name, default_branch)
#         "pr_details": List[
#             Dict[str, str]
#         ],  # List of {number, title, url} for merged PRs
#     },
#     tools={
#         "repo_owner": str,  # Owner of the source repository
#         "repo_name": str,  # Name of the source repository
#         "staking_key": str,  # Leader's staking key
#         "pub_key": str,  # Leader's public key
#         "staking_signature": str,  # Leader's staking signature
#         "public_signature": str,  # Leader's public signature
#         "head_branch": str,  # Head branch for the PR
#     },
# )
class CreatePullRequestPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="create_consolidated_pr",
            available_tools=[
                "read_file",
                "list_files",
                "create_leader_pull_request",
            ],
            conversation_id=conversation_id,
            name="Create Pull Request",
        )
