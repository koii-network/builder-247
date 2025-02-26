"""Module for file operations."""

import os
import shutil
from pathlib import Path
from src.tools.git_operations.implementations import commit_and_push
from git import Repo
from src.clients.types import ToolOutput


def _normalize_path(path: str) -> str:
    """Helper function to normalize paths by stripping leading slashes."""
    return path.lstrip("/")


def read_file(file_path: str) -> ToolOutput:
    """
    Read the contents of a file.

    Args:
        file_path (str): Path to the file to read

    Returns:
        ToolOutput: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - message (str): A human readable message
            - data (dict): The file contents if successful
            - error (str): Error message if unsuccessful
    """
    try:
        file_path = _normalize_path(file_path)
        full_path = Path(os.getcwd()) / file_path
        with open(full_path, "r") as f:
            content = f.read()
            return {
                "success": True,
                "message": f"Successfully read file {file_path}",
                "data": {"content": content},
                "error": None,
            }
    except FileNotFoundError:
        return {
            "success": False,
            "message": f"File not found: {file_path}",
            "data": None,
            "error": f"File not found: {file_path}",
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to read file",
            "data": None,
            "error": f"Error reading file: {str(e)}",
        }


def write_file(file_path: str, content: str, commit_message: str = None) -> ToolOutput:
    """Write file with directory creation and optional commit"""
    try:
        file_path = _normalize_path(file_path)
        full_path = Path(os.getcwd()) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w") as f:
            f.write(content)

        # If commit message provided, commit and push changes
        if commit_message:
            commit_result = commit_and_push(commit_message)
            if not commit_result["success"]:
                return commit_result

        return {
            "success": True,
            "message": f"Successfully wrote to file {file_path}",
            "data": {"path": file_path},
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to write file",
            "data": None,
            "error": str(e),
        }


def copy_file(source: str, destination: str, commit_message: str = None) -> ToolOutput:
    """Copy a file and optionally commit the change."""
    try:
        source = _normalize_path(source)
        destination = _normalize_path(destination)
        source_path = Path(os.getcwd()) / source
        dest_path = Path(os.getcwd()) / destination

        if not source_path.exists():
            return {
                "success": False,
                "message": "Source file not found",
                "data": None,
                "error": "Source file not found",
            }

        # Create destination directory if it doesn't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_path, dest_path)

        # If commit message provided, commit and push changes
        if commit_message:
            commit_result = commit_and_push(commit_message)
            if not commit_result["success"]:
                return commit_result

        return {
            "success": True,
            "message": f"Successfully copied file from {source} to {destination}",
            "data": {"source": source, "destination": destination},
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to copy file",
            "data": None,
            "error": str(e),
        }


def move_file(source: str, destination: str, commit_message: str = None) -> ToolOutput:
    """Move a file and optionally commit the change."""
    try:
        source = _normalize_path(source)
        destination = _normalize_path(destination)
        source_path = Path(os.getcwd()) / source
        dest_path = Path(os.getcwd()) / destination

        if not source_path.exists():
            return {
                "success": False,
                "message": "Source file not found",
                "data": None,
                "error": "Source file not found",
            }

        # Create destination directory if it doesn't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(source_path), str(dest_path))

        # If commit message provided, commit and push changes
        if commit_message:
            commit_result = commit_and_push(commit_message)
            if not commit_result["success"]:
                return commit_result

        return {
            "success": True,
            "message": f"Successfully moved file from {source} to {destination}",
            "data": {"source": source, "destination": destination},
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to move file",
            "data": None,
            "error": str(e),
        }


def rename_file(
    source: str, destination: str, commit_message: str = None
) -> ToolOutput:
    """Rename a file and optionally commit the change."""
    try:
        source = _normalize_path(source)
        destination = _normalize_path(destination)
        source_path = Path(os.getcwd()) / source
        dest_path = Path(os.getcwd()) / destination

        if not source_path.exists():
            return {
                "success": False,
                "message": f"Source file not found: {source}",
                "data": None,
                "error": f"Source file not found: {source}",
            }

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        os.rename(source_path, dest_path)

        # If commit message provided, commit and push changes
        if commit_message:
            commit_result = commit_and_push(commit_message)
            if not commit_result["success"]:
                return commit_result

        return {
            "success": True,
            "message": f"Successfully renamed file from {source} to {destination}",
            "data": {"source": source, "destination": destination},
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to rename file",
            "data": None,
            "error": f"Error renaming file: {str(e)}",
        }


def delete_file(file_path: str, commit_message: str = None) -> ToolOutput:
    """Delete a file and optionally commit the change."""
    try:
        file_path = _normalize_path(file_path)
        full_path = Path(os.getcwd()) / file_path

        if not full_path.exists():
            return {
                "success": False,
                "message": "File not found",
                "data": None,
                "error": "File not found",
            }

        os.remove(full_path)

        # If commit message provided, commit and push changes
        if commit_message:
            commit_result = commit_and_push(commit_message)
            if not commit_result["success"]:
                return commit_result

        return {
            "success": True,
            "message": f"Successfully deleted file: {file_path}",
            "data": {"path": file_path},
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to delete file",
            "data": None,
            "error": str(e),
        }


def list_files(directory: str) -> ToolOutput:
    """
    Return a list of all files in the specified directory and its subdirectories,
    excluding .git directory and respecting .gitignore.

    Parameters:
    directory (str or Path): The directory to search for files.

    Returns:
        ToolOutput: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - message (str): A human readable message
            - data (dict): Dictionary containing list of files if successful
            - error (str): Error message if unsuccessful
    """
    try:
        directory = _normalize_path(directory)
        directory = Path(os.getcwd()) / directory

        if not directory.exists() or not directory.is_dir():
            return {
                "success": False,
                "message": f"The directory '{directory}' does not exist",
                "data": None,
                "error": f"The directory '{directory}' does not exist",
            }

        # Use git to list all tracked and untracked files, respecting .gitignore
        repo = Repo(directory)

        # Get tracked files
        tracked_files = set(repo.git.ls_files().splitlines())

        # Get untracked files (excluding .gitignored)
        untracked_files = set(
            repo.git.ls_files("--others", "--exclude-standard").splitlines()
        )

        # Combine and filter out .git directory
        all_files = tracked_files.union(untracked_files)
        files = sorted([f for f in all_files if not f.startswith(".git/")])

        return {
            "success": True,
            "message": f"Found {len(files)} files in {directory}",
            "data": {"files": files},
            "error": None,
        }

    except (FileNotFoundError, OSError) as e:  # Catch specific file-related exceptions
        return {
            "success": False,
            "message": "Failed to list files",
            "data": None,
            "error": str(e),
        }


def create_directory(path: str) -> ToolOutput:
    """Create a directory and any necessary parent directories.

    Args:
        path (str): Path to the directory to create

    Returns:
        ToolOutput: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - message (str): A human readable message
            - error (str): Error message if unsuccessful
    """
    try:
        path = _normalize_path(path)
        full_path = Path(os.getcwd()) / path
        full_path.mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "message": f"Created directory: {path}",
            "data": {"path": path},
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to create directory",
            "data": None,
            "error": f"Failed to create directory: {str(e)}",
        }
