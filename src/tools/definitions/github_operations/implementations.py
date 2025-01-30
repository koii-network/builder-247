"""GitHub operations tool implementations."""

from ...github_operations import (
    get_pr_template,
    fork_repository,
    sync_fork,
    create_pull_request,
    check_fork_exists,
)

TOOL_IMPLEMENTATIONS = {
    "get_pr_template": get_pr_template,
    "fork_repository": fork_repository,
    "sync_fork": sync_fork,
    "create_pull_request": create_pull_request,
    "check_fork_exists": check_fork_exists,
}
