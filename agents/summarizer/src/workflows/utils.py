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


def setup_repo_directory():
    """Set up a unique repository directory.

    Returns:
        tuple: (repo_path, original_dir)
    """
    # Generate sequential repo path
    # TODO THIS IS A TEMPORARY FIX
    base_dir = os.path.abspath("/app/repos")
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
