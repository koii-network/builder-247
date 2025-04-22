from prometheus_swarm.tools.file_operations.implementations import (
    read_file,
    write_file,
    copy_file,
    move_file,
    rename_file,
    delete_file,
    list_files,
    create_directory,
)

DEFINITIONS = {
    "read_file": {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read",
                },
            },
            "required": ["file_path"],
        },
        "function": read_file,
    },
    "write_file": {
        "name": "write_file",
        "description": "Write content to a file and commit the change.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message describing the change",
                },
            },
            "required": ["file_path", "content", "commit_message"],
        },
        "function": write_file,
    },
    "create_directory": {
        "name": "create_directory",
        "description": "Create a directory and any necessary parent directories.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to create",
                },
            },
            "required": ["path"],
        },
        "function": create_directory,
    },
    "copy_file": {
        "name": "copy_file",
        "description": "Copy a file and commit the change.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Path to the source file"},
                "destination": {
                    "type": "string",
                    "description": "Path to the destination file",
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message describing the change",
                },
            },
            "required": ["source", "destination", "commit_message"],
        },
        "function": copy_file,
    },
    "move_file": {
        "name": "move_file",
        "description": "Move a file and commit the change.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Path to the source file"},
                "destination": {
                    "type": "string",
                    "description": "Path to the destination file",
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message describing the change",
                },
            },
            "required": ["source", "destination", "commit_message"],
        },
        "function": move_file,
    },
    "rename_file": {
        "name": "rename_file",
        "description": "Rename a file and commit the change.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Current file path"},
                "destination": {"type": "string", "description": "New file path"},
                "commit_message": {
                    "type": "string",
                    "description": "Commit message describing the change",
                },
            },
            "required": ["source", "destination", "commit_message"],
        },
        "function": rename_file,
    },
    "delete_file": {
        "name": "delete_file",
        "description": "Delete a file and commit the change.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to delete",
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message describing the change",
                },
            },
            "required": ["file_path", "commit_message"],
        },
        "function": delete_file,
    },
    "list_files": {
        "name": "list_files",
        "description": "List all files in a directory and its subdirectories.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to list files from",
                },
            },
            "required": ["directory"],
        },
        "function": list_files,
    },
}
