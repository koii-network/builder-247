"""File operations tool implementations."""

from src.tools.file_operations import (
    read_file,
    write_file,
    copy_file,
    move_file,
    rename_file,
    delete_file,
)

TOOL_IMPLEMENTATIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "copy_file": copy_file,
    "move_file": move_file,
    "rename_file": rename_file,
    "delete_file": delete_file,
}
