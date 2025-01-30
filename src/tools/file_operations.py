"""Module for file operations."""

import os
import shutil
from typing import Dict, Any
from pathlib import Path
from src.tools.execute_command import execute_command


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
        with open(file_path, "r") as f:
            return {"success": True, "content": f.read()}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {file_path}"}
    except Exception as e:
        return {"success": False, "error": f"Error reading file: {str(e)}"}


def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file.

    Args:
        file_path (str): Path to the file to write
        content (str): Content to write to the file

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - error (str): Error message if unsuccessful
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": f"Error writing file: {str(e)}"}


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
        if not os.path.exists(source):
            return {"success": False, "error": "Source file not found"}

        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        shutil.copy2(source, destination)
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
        if not os.path.exists(source):
            return {"success": False, "error": "Source file not found"}

        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        result = execute_command(f"mv {source} {destination}")
        if result[2] != 0:
            raise Exception("Failed to move file")
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
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        os.rename(source, destination)
        return {"success": True}
    except FileNotFoundError:
        return {"success": False, "error": f"Source file not found: {source}"}
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
        if not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}

        result = execute_command(f"rm {file_path}")
        if result[2] != 0:
            raise Exception("Failed to delete file")
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
    directory = Path(directory)

    # Check if the directory exists
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"The directory '{directory}' does not exist.")

    # Check if the provided path is absolute
    if not directory.is_absolute():
        directory = Path.cwd() / directory

    return [str(file.relative_to(directory)) for file in directory.rglob('*') if file.is_file()]
