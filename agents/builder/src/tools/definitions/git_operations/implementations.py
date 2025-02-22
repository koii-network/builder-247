"""Git operations tool implementations."""

from src.tools.git_operations import (
    init_repository,
    clone_repository,
    create_branch,
    checkout_branch,
    get_current_branch,
    list_branches,
    add_remote,
    fetch_remote,
    pull_remote,
    check_for_conflicts,
    get_conflict_info,
    resolve_conflict,
    create_merge_commit,
    commit_and_push,
    can_access_repository,
)

TOOL_IMPLEMENTATIONS = {
    "init_repository": init_repository,
    "clone_repository": clone_repository,
    "create_branch": create_branch,
    "checkout_branch": checkout_branch,
    "get_current_branch": get_current_branch,
    "list_branches": list_branches,
    "add_remote": add_remote,
    "fetch_remote": fetch_remote,
    "pull_remote": pull_remote,
    "check_for_conflicts": check_for_conflicts,
    "get_conflict_info": get_conflict_info,
    "resolve_conflict": resolve_conflict,
    "create_merge_commit": create_merge_commit,
    "commit_and_push": commit_and_push,
    "can_access_repository": can_access_repository,
}
