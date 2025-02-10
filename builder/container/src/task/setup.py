# check if a fork exists, sync if it does, create a fork if it doesn't
from dotenv import load_dotenv
import os
from src.anthropic_client import AnthropicClient
from src.tools.github_operations import check_fork_exists, fork_repository, sync_fork
import shutil


def setup_repository(repo_owner, repo_name, repo_path):
    """Check if the branch exists, sync or create the branch"""
    # Check if the branch exists
    print("Checking if fork exists")
    fork_check = check_fork_exists(repo_owner, repo_name)
    if fork_check["success"] and fork_check["exists"]:
        print("Fork exists")
        # If the branch exists, ensure the path exists
        if not os.path.exists(repo_path):
            print("Path does not exist, cloning repository")
            # If the path does not exist, clone the repository first
            fork_result = fork_repository(f"{repo_owner}/{repo_name}", repo_path)
            if not fork_result["success"]:
                raise Exception(f"Failed to create fork: {fork_result['error']}")

        # Sync it
        sync_result = sync_fork(repo_path, "master")
        print("Sync result: ", sync_result)
        if not sync_result["success"]:
            raise Exception(f"Failed to sync fork: {sync_result['error']}")
    else:
        print("Fork does not exist")
        # If the branch does not exist, create it
        # Check and delete existing directory before cloning
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        print("Forking repository")
        fork_result = fork_repository(f"{repo_owner}/{repo_name}", repo_path)
        print("Fork result: ", fork_result)
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
