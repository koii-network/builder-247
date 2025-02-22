"""GitHub operations tool implementations."""

from src.tools.github_operations import (
    fork_repository,
    sync_fork,
    check_fork_exists,
    create_pull_request,
    review_pull_request,
)

TOOL_IMPLEMENTATIONS = {
    "fork_repository": fork_repository,
    "sync_fork": sync_fork,
    "check_fork_exists": check_fork_exists,
    "create_pull_request": create_pull_request,
    "review_pull_request": review_pull_request,
}
