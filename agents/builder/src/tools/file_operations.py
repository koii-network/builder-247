"""Module for file operations."""

import os
import shutil
from typing import Dict, Any
from pathlib import Path


def _normalize_path(path: str) -> str:
    """Helper function to normalize paths by stripping leading slashes."""
    return path.lstrip("/")


def read_file(file_path: str) -> Dict[str, Any]:
    """
    Read the contents of a file.

    Args:
        file_path (str): Path to the file to read

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - content (str): The file contents if successful
            - error (str): Error message if unsuccessful
    """
    try:
        file_path = _normalize_path(file_path)
        full_path = Path(os.getcwd()) / file_path
        with open(full_path, "r") as f:
            return {"success": True, "content": f.read()}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {file_path}"}
    except Exception as e:
        return {"success": False, "error": f"Error reading file: {str(e)}"}


def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """Write file with directory creation"""
    try:
        file_path = _normalize_path(file_path)
        full_path = Path(os.getcwd()) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w") as f:
            f.write(content)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def copy_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Copy a file from source to destination.

    Args:
        source (str): Path to the source file
        destination (str): Path to the destination file

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - error (str): Error message if unsuccessful
    """
    try:
        source = _normalize_path(source)
        destination = _normalize_path(destination)
        source_path = Path(os.getcwd()) / source
        dest_path = Path(os.getcwd()) / destination

        if not source_path.exists():
            return {"success": False, "error": "Source file not found"}

        # Create destination directory if it doesn't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_path, dest_path)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Move a file from source to destination.

    Args:
        source (str): Path to the source file
        destination (str): Path to the destination file

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - error (str): Error message if unsuccessful
    """
    try:
        source = _normalize_path(source)
        destination = _normalize_path(destination)
        source_path = Path(os.getcwd()) / source
        dest_path = Path(os.getcwd()) / destination

        if not source_path.exists():
            return {"success": False, "error": "Source file not found"}

        # Create destination directory if it doesn't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(source_path), str(dest_path))
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def rename_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Rename a file from source to destination.

    Args:
        source (str): Current file path
        destination (str): New file path

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - error (str): Error message if unsuccessful
    """
    try:
        source = _normalize_path(source)
        destination = _normalize_path(destination)
        source_path = Path(os.getcwd()) / source
        dest_path = Path(os.getcwd()) / destination

        if not source_path.exists():
            return {"success": False, "error": f"Source file not found: {source}"}

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        os.rename(source_path, dest_path)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": f"Error renaming file: {str(e)}"}


def delete_file(file_path: str) -> Dict[str, Any]:
    """
    Delete a file.

    Args:
        file_path (str): Path to the file to delete

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - error (str): Error message if unsuccessful
    """
    try:
        file_path = _normalize_path(file_path)
        full_path = Path(os.getcwd()) / file_path

        if not full_path.exists():
            return {"success": False, "error": "File not found"}

        os.remove(full_path)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files(directory: str) -> list:
    """
    Return a list of all files in the specified directory and its subdirectories.

    Parameters:
    directory (str or Path): The directory to search for files.

    Returns:
    list: A list of file paths relative to the specified directory or CWD.
    """
    try:
        directory = _normalize_path(directory)
        directory = Path(os.getcwd()) / directory

        if not directory.exists() or not directory.is_dir():
            raise FileNotFoundError(f"The directory '{directory}' does not exist.")

        return [
            str(file.relative_to(directory))
            for file in directory.rglob("*")
            if file.is_file()
        ]
    except (FileNotFoundError, OSError):  # Catch specific file-related exceptions
        return []


def create_file(file_path: str, content: str) -> dict:
    """Create a new file with specified content."""
    try:
        file_path = _normalize_path(file_path)
        full_path = Path(os.getcwd()) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w") as f:
            f.write(content)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
