# check if a fork exists, sync if it does, create a fork if it doesn't
from dotenv import load_dotenv
import os
from src.anthropic_client import AnthropicClient
from src.tools.github_operations import check_fork_exists, fork_repository, sync_fork
import shutil


def setup_repository(repo_owner, repo_name, repo_path):
    """Check if the branch exists, sync or create the branch"""
    # Convert to absolute path
    repo_path = os.path.abspath(repo_path)
    print(f"Using absolute repository path: {repo_path}")

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(repo_path), exist_ok=True)

    # Check if the branch exists
    print(f"Checking if fork exists at {repo_path}")
    fork_check = check_fork_exists(repo_owner, repo_name)

    if fork_check["success"] and fork_check["exists"]:
        print("Fork exists")
        if not os.path.exists(repo_path):
            print("Cloning repository...")
            clone_result = fork_repository(f"{repo_owner}/{repo_name}", repo_path)
            if not clone_result["success"]:
                raise Exception(f"Cloning failed: {clone_result['error']}")
        else:
            print("Updating existing repository...")
            sync_result = sync_fork(repo_path, "main")
            if not sync_result["success"]:
                raise Exception(f"Sync failed: {sync_result['error']}")
    else:
        print("Creating new fork")
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        print(f"Forking to {repo_path}")
        fork_result = fork_repository(f"{repo_owner}/{repo_name}", repo_path)
        if not fork_result["success"]:
            raise Exception(f"Forking failed: {fork_result['error']}")

    # Verify repository exists
    if not os.path.exists(repo_path):
        raise Exception(f"Repository path not created: {repo_path}")

    return repo_path


def setup_client(repo_path: str):
    """
    Setup the anthropic client with repository context
    """
    load_dotenv()
    api_key = os.environ.get("CLAUDE_API_KEY")
    client = AnthropicClient(
        api_key=api_key,
        default_headers={"X-API-Key": os.environ.get("MIDDLE_SERVER_API_KEY")},
        working_directory=repo_path,
    )
    client.register_tools_from_directory("./src/tools/definitions/execute_command")
    client.register_tools_from_directory("./src/tools/definitions/file_operations")
    client.register_tools_from_directory("./src/tools/definitions/git_operations")
    client.register_tools_from_directory("./src/tools/definitions/github_operations")
    return client
