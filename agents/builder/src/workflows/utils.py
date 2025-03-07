"""Centralized workflow utilities."""

import os
import shutil
from github import Github
from git import Repo
from src.utils.logging import log_key_value, log_error
from src.tools.file_operations.implementations import list_files


def check_required_env_vars(env_vars: list[str]):
    """Check if all required environment variables are set."""
    missing_vars = [var for var in env_vars if not os.environ.get(var)]

    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please ensure these are set in your .env file or environment."
        )


def validate_github_auth(github_token: str, github_username: str):
    """Validate GitHub authentication."""
    try:
        gh = Github(github_token)
        user = gh.get_user()
        username = user.login
        if username != github_username:
            raise ValueError(
                f"GitHub token belongs to {username}, but GITHUB_USERNAME is set to {github_username}"
            )
        log_key_value("Successfully authenticated as", username)
    except Exception as e:
        log_error(e, "GitHub authentication failed")
        raise RuntimeError(str(e))


def setup_repo_directory() -> tuple[str, str]:
    """Set up a unique repository directory.

    Returns:
        tuple: (repo_path, original_dir)
    """
    # Generate sequential repo path
    base_dir = os.path.abspath("./repos")
    os.makedirs(base_dir, exist_ok=True)

    counter = 0
    while True:
        candidate_path = os.path.join(base_dir, f"repo_{counter}")
        if not os.path.exists(candidate_path):
            repo_path = candidate_path
            break
        counter += 1

    # Clean existing repository
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    # Create parent directory
    os.makedirs(os.path.dirname(repo_path), exist_ok=True)

    # Save original directory
    original_dir = os.getcwd()

    return repo_path, original_dir


def setup_git_user_config(repo_path):
    """Configure Git user info for the repository."""
    repo = Repo(repo_path)
    with repo.config_writer() as config:
        config.set_value("user", "name", os.environ["GITHUB_USERNAME"])
        config.set_value(
            "user",
            "email",
            f"{os.environ['GITHUB_USERNAME']}@users.noreply.github.com",
        )


def cleanup_repo_directory(original_dir, repo_path):
    """Clean up repository directory and return to original directory.

    Args:
        original_dir: Original directory to return to
        repo_path: Repository path to clean up
    """
    os.chdir(original_dir)
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)


def get_current_files():
    """Get current files in repository."""
    files_result = list_files(".")
    if not files_result["success"]:
        raise Exception(f"Failed to get file list: {files_result['message']}")

    return files_result["data"]["files"]


def fork_repository(repo_full_name: str) -> dict:
    """Fork a repository.

    Args:
        repo_full_name: Full name of repository (owner/repo)

    Returns:
        dict: Result with success status and fork URL if successful
    """
    try:
        gh = Github(os.environ["GITHUB_TOKEN"])
        source_repo = gh.get_repo(repo_full_name)

        # Get authenticated user
        user = gh.get_user()
        username = user.login

        # Check if fork already exists
        try:
            fork = gh.get_repo(f"{username}/{source_repo.name}")
            log_key_value("Using existing fork", fork.html_url)
        except Exception:
            # Create fork if it doesn't exist
            fork = user.create_fork(source_repo)
            log_key_value("Created new fork", fork.html_url)

        # Wait for fork to be ready
        log_key_value("Waiting for fork to be ready", "")
        max_retries = 10
        for _ in range(max_retries):
            try:
                fork.get_commits().get_page(0)
                break
            except Exception:
                import time

                time.sleep(1)

        return {
            "success": True,
            "message": f"Successfully forked {repo_full_name}",
            "data": {
                "fork_url": fork.html_url,
                "owner": username,
                "repo": source_repo.name,
            },
        }

    except Exception as e:
        error_msg = str(e)
        log_error(e, "Fork failed")
        return {
            "success": False,
            "message": "Failed to fork repository",
            "data": None,
            "error": error_msg,
        }


def clone_repository(repo_url: str, repo_path: str) -> dict:
    """Clone a repository directly without forking.

    Args:
        repo_url: URL of the repository to clone
        repo_path: Local path to clone to

    Returns:
        dict: Result with success status and error message if any
    """
    try:
        # Add GitHub token to URL for authentication
        token = os.getenv("GITHUB_TOKEN")
        auth_url = repo_url.replace("https://", f"https://{token}@")

        # Clone the repository
        log_key_value("Cloning repository", repo_url)
        log_key_value("Clone path", repo_path)

        repo = Repo.clone_from(auth_url, repo_path)

        return {
            "success": True,
            "message": f"Successfully cloned repository to {repo_path}",
            "data": {"clone_path": repo_path, "repo": repo},
        }
    except Exception as e:
        error_msg = str(e)
        log_error(e, "Clone failed")
        return {
            "success": False,
            "message": "Failed to clone repository",
            "data": None,
            "error": error_msg,
        }


def setup_repository(repo_url: str, clone_only: bool = False) -> dict:
    """Set up a repository by forking (optional) and cloning.

    Args:
        repo_url: URL of the repository (e.g., https://github.com/owner/repo)
        clone_only: If True, just clone without forking. Defaults to False.

    Returns:
        dict: Result with success status, repository details, and paths
    """
    try:
        # Extract owner/repo from URL
        parts = repo_url.strip("/").split("/")
        repo_owner = parts[-2]
        repo_name = parts[-1]
        repo_full_name = f"{repo_owner}/{repo_name}"

        # Set up directory
        repo_path, original_dir = setup_repo_directory()

        # Fork if needed
        if not clone_only:
            fork_result = fork_repository(repo_full_name)
            if not fork_result["success"]:
                cleanup_repo_directory(original_dir, repo_path)
                return fork_result
            clone_url = fork_result["data"]["fork_url"]
        else:
            clone_url = repo_url

        # Clone the repository
        clone_result = clone_repository(clone_url, repo_path)
        if not clone_result["success"]:
            cleanup_repo_directory(original_dir, repo_path)
            return clone_result

        return {
            "success": True,
            "message": "Successfully set up repository",
            "data": {
                "repo_path": repo_path,
                "original_dir": original_dir,
                "clone_url": clone_url,
                "git_repo": clone_result["data"]["repo"],
                **(fork_result["data"] if not clone_only else {}),
            },
        }

    except Exception as e:
        error_msg = str(e)
        log_error(e, "Repository setup failed")
        if locals().get("repo_path") and locals().get("original_dir"):
            cleanup_repo_directory(original_dir, repo_path)
        return {
            "success": False,
            "message": "Failed to set up repository",
            "data": None,
            "error": error_msg,
        }
