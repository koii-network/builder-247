# check if a fork exists, sync if it does, create a fork if it doesn't
from dotenv import load_dotenv
import os
import tempfile
from pathlib import Path
from src.anthropic_client import AnthropicClient
from src.tools.github_operations import check_fork_exists, fork_repository, sync_fork, create_pull_request
from src.tools.git_operations import create_branch, checkout_branch, make_commit, push_remote, get_current_branch
from src.tools.file_operations import read_file, write_file, move_file, copy_file, rename_file, delete_file, list_files
import shutil
from anthropic.types import (
    ToolUseBlock,
)
from src.get_file_list import get_file_list

def setup_repository(repo_owner, repo_name, repo_path):
    """Check if the branch exists, sync or create the branch"""
    # Check if the branch exists
    fork_check = check_fork_exists(repo_owner, repo_name)
    if fork_check["success"] and fork_check["exists"]:
        # If the branch exists, ensure the path exists
        if not os.path.exists(repo_path):
            # If the path does not exist, clone the repository first
            fork_result = fork_repository(f"{repo_owner}/{repo_name}", repo_path)
            if not fork_result["success"]:
                raise Exception(f"Failed to create fork: {fork_result['error']}")
            
        # Sync it
        sync_result = sync_fork(repo_path, "master")
        if not sync_result["success"]:
            raise Exception(f"Failed to sync fork: {sync_result['error']}")
    else:
        # If the branch does not exist, create it
        # Check and delete existing directory before cloning
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        
        fork_result = fork_repository(f"{repo_owner}/{repo_name}", repo_path)
        if not fork_result["success"]:
            raise Exception(f"Failed to create fork: {fork_result['error']}")
        
        # Add debug information
        if not os.path.exists(repo_path):
            raise Exception(f"Cloning failed, path does not exist: {repo_path}")
        
    return repo_path

def setup_client():
    """
    Setup the anthropic client
    """
    load_dotenv()
    api_key = os.environ.get("CLAUDE_API_KEY")

    client = AnthropicClient(api_key=api_key)
    client.register_tools_from_directory("./src/tools/definitions/execute_command")
    client.register_tools_from_directory("./src/tools/definitions/file_operations")
    client.register_tools_from_directory("./src/tools/definitions/git_operations")
    client.register_tools_from_directory("./src/tools/definitions/github_operations")
    return client
