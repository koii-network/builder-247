"""Module for file operations."""

import shutil
from typing import Dict, Any, List
from pathlib import Path
from agents.builder.src.tools.execute_command.tools import execute_command


def ensure_relative_path(path: str) -> Path:
    """Convert the path to be relative to the current working directory."""
    if path.startswith("/"):
        path = path[1:]  # Remove leading slash to treat as relative
    return Path.cwd() / path


def read_file(file_path: str) -> Dict[str, Any]:
    """Read the contents of a file."""
    try:
        file_path = ensure_relative_path(file_path)
        with file_path.open("r") as f:
            return {"success": True, "content": f.read()}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {file_path}"}
    except Exception as e:
        return {"success": False, "error": f"Error reading file: {str(e)}"}


def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """Write file with directory creation."""
    try:
        file_path = ensure_relative_path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w") as f:
            f.write(content)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def copy_file(source: str, destination: str) -> Dict[str, Any]:
    """Copy a file from source to destination."""
    try:
        source_path = ensure_relative_path(source)
        destination_path = ensure_relative_path(destination)

        if not source_path.exists():
            return {"success": False, "error": "Source file not found"}

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_file(source: str, destination: str) -> Dict[str, Any]:
    """Move a file from source to destination."""
    try:
        source_path = ensure_relative_path(source)
        destination_path = ensure_relative_path(destination)

        if not source_path.exists():
            return {"success": False, "error": "Source file not found"}

        destination_path.parent.mkdir(parents=True, exist_ok=True)

        result = execute_command(f"mv {source_path} {destination_path}")
        if result[2] != 0:
            raise Exception("Failed to move file")
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def rename_file(source: str, destination: str) -> Dict[str, Any]:
    """Rename a file from source to destination."""
    try:
        source_path = ensure_relative_path(source)
        destination_path = ensure_relative_path(destination)

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(destination_path)
        return {"success": True}
    except FileNotFoundError:
        return {"success": False, "error": f"Source file not found: {source}"}
    except Exception as e:
        return {"success": False, "error": f"Error renaming file: {str(e)}"}


def delete_file(file_path: str) -> Dict[str, Any]:
    """Delete a file."""
    try:
        file_path = ensure_relative_path(file_path)
        if not file_path.exists():
            return {"success": False, "error": "File not found"}

        result = execute_command(f"rm {file_path}")
        if result[2] != 0:
            raise Exception("Failed to delete file")
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files(directory: str) -> List[str]:
    """Return a list of all files in the specified directory and its subdirectories."""
    try:
        directory_path = ensure_relative_path(directory)

        if not directory_path.exists() or not directory_path.is_dir():
            raise FileNotFoundError(f"The directory '{directory}' does not exist.")

        return [
            str(file.relative_to(directory_path))
            for file in directory_path.rglob("*")
            if file.is_file()
        ]
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_file(file_path: str, content: str) -> Dict[str, Any]:
    """Create a new file with specified content."""
    try:
        full_path = ensure_relative_path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with full_path.open("w") as f:
            f.write(content)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
