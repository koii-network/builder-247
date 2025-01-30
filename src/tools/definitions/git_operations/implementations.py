"""Git operations tool implementations."""

from ...git_operations import (
    check_for_conflicts,
    get_conflict_info,
    resolve_conflict,
    create_merge_commit,
)

TOOL_IMPLEMENTATIONS = {
    "check_for_conflicts": check_for_conflicts,
    "get_conflict_info": get_conflict_info,
    "resolve_conflict": resolve_conflict,
    "create_merge_commit": create_merge_commit,
}
