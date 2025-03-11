"""Module for Git operations."""

import os
import shutil
from pathlib import Path
from git import Repo, GitCommandError
from src.utils.logging import log_key_value, log_error
from src.types import ToolOutput

import time


def _get_repo(repo_path: str) -> Repo:
    """
    Get a GitPython Repo instance from a path.

    Args:
        repo_path (str): Path to the git repository

    Returns:
        Repo: The GitPython Repo instance

    Raises:
        Exception: If the path is not a git repository
    """
    if not os.path.exists(repo_path):
        raise Exception(f"Path does not exist: {repo_path}")
    return Repo(repo_path)


def init_repository(
    path: str, user_name: str = None, user_email: str = None
) -> ToolOutput:
    """
    Initialize a new Git repository.

    Args:
        path (str): Path where to initialize the repository
        user_name (str, optional): Git user name to configure
        user_email (str, optional): Git user email to configure

    Returns:
        ToolOutput: Result of the operation
    """
    try:
        log_key_value("Initializing repository at", path)
        repo = Repo.init(path)
        if user_name:
            repo.config_writer().set_value("user", "name", user_name).release()
        if user_email:
            repo.config_writer().set_value("user", "email", user_email).release()
        return {
            "success": True,
            "message": f"Successfully initialized repository at {path}",
            "data": {"path": path},
        }
    except Exception as e:
        log_error(e, "Failed to initialize repository")
        return {
            "success": False,
            "message": str(e),
            "data": None,
        }


def clone_repository(
    url: str, path: str, user_name: str = None, user_email: str = None
) -> ToolOutput:
    """
    Clone a Git repository with proper path handling and cleanup.

    Returns:
        ToolOutput: Result of the operation
    """
    try:
        log_key_value("Cloning repository to", os.path.abspath(path))
        log_key_value("Source URL", url)

        # Clean up existing path if it exists
        if os.path.exists(path):
            log_key_value("Removing existing path", path)
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

        # Create target directory
        log_key_value("Creating directory", path)
        os.makedirs(path, exist_ok=True)

        # Add GitHub token authentication
        if "github.com" in url and "GITHUB_TOKEN" in os.environ:
            token = os.environ["GITHUB_TOKEN"]
            log_key_value(
                "Adding GitHub token authentication", "Using token for authentication"
            )
            if url.startswith("https://"):
                url = url.replace("https://", f"https://{token}@")
            elif url.startswith("git@"):
                url = f"https://{token}@github.com/{url.split(':', 1)[1]}"
            log_key_value("Modified URL", url)

        # Clone repository
        log_key_value("Starting clone operation", "Cloning repository...")
        repo = Repo.clone_from(url, path)
        log_key_value("Clone completed", "successfully")

        # Configure user information
        if user_name or user_email:
            log_key_value("Configuring user", f"{user_name} <{user_email}>")
            with repo.config_writer() as config:
                if user_name:
                    config.set_value("user", "name", user_name)
                if user_email:
                    config.set_value("user", "email", user_email)

        # Enforce GitHub Actions user configuration
        with repo.config_writer() as config:
            config.set_value("user", "name", os.environ["GITHUB_USERNAME"])
            config.set_value(
                "user",
                "email",
                f"{os.environ['GITHUB_USERNAME']}@users.noreply.github.com",
            )

        return {
            "success": True,
            "message": f"Successfully cloned repository to {path}",
            "data": {"path": path, "url": url},
        }
    except GitCommandError as e:
        error_msg = f"Clone failed with error: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def create_branch(branch_base: str) -> ToolOutput:
    """Create branch with automatic timestamp suffix"""
    try:
        # Check for GitHub token first
        if "GITHUB_TOKEN" not in os.environ:
            return {
                "success": False,
                "message": "GitHub token not found in environment. Please set GITHUB_TOKEN environment variable.",
                "data": None,
            }

        # Validate base name
        if not branch_base:
            return {
                "success": False,
                "message": "Missing branch base name",
                "data": None,
            }

        # Clean branch base name - remove special characters and spaces
        branch_base = branch_base.strip().lower()
        branch_base = "".join(
            c if c.isalnum() or c in "-_" else "-" for c in branch_base
        )
        if not branch_base:
            return {
                "success": False,
                "message": "Invalid branch name after cleaning",
                "data": None,
            }

        # Generate branch name
        timestamp = int(time.time())
        branch_name = f"{branch_base}-{timestamp}"

        repo = Repo(os.getcwd())
        log_key_value("Creating branch", f"'{branch_name}' in {repo.working_dir}")

        # Check if we're in a git repo
        if not os.path.exists(os.path.join(repo.working_dir, ".git")):
            return {
                "success": False,
                "message": "Not a git repository",
                "data": None,
            }

        # Check if we have a remote named 'origin'
        try:
            origin = repo.remote("origin")
            # Update origin URL with token
            url = origin.url
            if "github.com" in url:
                token = os.environ["GITHUB_TOKEN"]
                if url.startswith("https://"):
                    new_url = url.replace("https://", f"https://{token}@")
                elif url.startswith("git@"):
                    new_url = f"https://{token}@github.com/{url.split(':', 1)[1]}"
                origin.set_url(new_url)
        except ValueError:
            return {
                "success": False,
                "message": "No 'origin' remote found",
                "data": None,
            }

        # Create and checkout branch
        try:
            repo.git.checkout("-b", branch_name)
        except GitCommandError as e:
            if "already exists" in str(e):
                return {
                    "success": False,
                    "message": f"Branch '{branch_name}' already exists",
                    "data": None,
                }
            raise

        # Verify branch exists
        if branch_name not in repo.heads:
            return {
                "success": False,
                "message": f"Failed to create branch: {branch_name}",
                "data": None,
            }

        # Configure upstream tracking
        try:
            repo.git.push("--set-upstream", "origin", branch_name)
        except GitCommandError as e:
            # Try to delete the local branch since push failed
            try:
                repo.git.checkout("main")
                repo.git.branch("-D", branch_name)
            except GitCommandError:
                pass

            error_msg = str(e)
            if "Permission denied" in error_msg:
                return {
                    "success": False,
                    "message": (
                        "Permission denied pushing to remote. "
                        "Please check your GitHub token has the correct permissions."
                    ),
                    "data": None,
                }
            elif "Authentication failed" in error_msg:
                return {
                    "success": False,
                    "message": (
                        "Authentication failed. "
                        "Please check your GitHub token is valid and has the correct permissions."
                    ),
                    "data": None,
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to push branch: {error_msg}",
                    "data": None,
                }

        return {
            "success": True,
            "message": f"Created branch {branch_name}",
            "data": {
                "branch_name": branch_name,
                "message": f"Created branch {branch_name}",
            },
        }
    except GitCommandError as e:
        error_msg = f"Git error: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def checkout_branch(branch_name: str) -> ToolOutput:
    """Check out an existing branch in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        log_key_value("Checking out branch", branch_name)
        branch = repo.heads[branch_name]
        branch.checkout()
        return {
            "success": True,
            "message": f"Successfully checked out branch {branch_name}",
            "data": {"branch": branch_name},
        }
    except GitCommandError as e:
        error_msg = f"Failed to checkout branch: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def commit_and_push(message: str) -> ToolOutput:
    """Commit all changes and push to remote."""
    try:
        repo = Repo(os.getcwd())
        log_key_value("Committing changes", message)

        # Stage all changes
        repo.git.add(A=True)

        # Create commit
        commit = repo.index.commit(message)

        # Try to push, with automatic pull if needed
        try:
            repo.git.push("origin", repo.active_branch.name)
        except GitCommandError:
            # If push failed, pull and try again
            repo.git.pull("origin", repo.active_branch.name)
            repo.git.push("origin", repo.active_branch.name)

        return {
            "success": True,
            "message": f"Changes committed and pushed: {message}",
            "data": {"commit_hash": commit.hexsha, "message": message},
        }
    except GitCommandError as e:
        error_msg = f"Failed to commit and push: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def get_current_branch() -> ToolOutput:
    """Get the current branch name in the working directory"""
    try:
        repo = Repo(os.getcwd())
        branch = repo.active_branch.name
        log_key_value("Current branch", branch)
        return {
            "success": True,
            "message": f"Current branch is {branch}",
            "data": {"branch": branch},
        }
    except GitCommandError as e:
        error_msg = f"Failed to get current branch: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def list_branches() -> ToolOutput:
    """List all branches in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        branches = [head.name for head in repo.heads]
        log_key_value("Branches", ", ".join(branches))
        return {
            "success": True,
            "message": f"Found {len(branches)} branches",
            "data": {"branches": branches},
        }
    except GitCommandError as e:
        error_msg = f"Failed to list branches: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def add_remote(name: str, url: str) -> ToolOutput:
    """Add a remote to the current repository."""
    try:
        repo_path = os.getcwd()
        # Insert GitHub token authentication logic
        repo = _get_repo(repo_path)
        log_key_value("Adding remote", f"{name} -> {url}")
        repo.create_remote(name, url)
        return {
            "success": True,
            "message": f"Successfully added remote {name}",
            "data": {"name": name, "url": url},
        }
    except GitCommandError as e:
        error_msg = f"Failed to add remote: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def fetch_remote(repo_path: str, remote_name: str) -> ToolOutput:
    """Fetch from a remote repository.

    Args:
        repo_path (str): Path to the git repository
        remote_name (str): Name of the remote to fetch from

    Returns:
        ToolOutput: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - message (str): A human readable message
            - data (dict): None
    """
    try:
        repo = _get_repo(repo_path)
        repo.git.fetch(remote_name)
        return {
            "success": True,
            "message": f"Successfully fetched from {remote_name}",
            "data": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to fetch from {remote_name}: {str(e)}",
            "data": None,
        }


def pull_remote(remote_name: str = "origin", branch: str = None) -> ToolOutput:
    """Pull changes with explicit branch specification."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        branch = branch or repo.active_branch.name
        log_key_value("Pulling from remote", f"{remote_name}/{branch}")

        repo.git.pull(remote_name, branch, "--allow-unrelated-histories")

        # Check for conflicts after pull
        if check_for_conflicts()["has_conflicts"]:
            return {
                "success": False,
                "message": "Merge conflict detected after pull",
                "data": None,
            }

        return {
            "success": True,
            "message": f"Successfully pulled from {remote_name}/{branch}",
            "data": {"remote": remote_name, "branch": branch},
        }
    except GitCommandError as e:
        error_msg = f"Failed to pull changes: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def can_access_repository(repo_url: str) -> ToolOutput:
    """Check if a git repository is accessible."""
    try:
        log_key_value("Checking access to", repo_url)
        # Use GitPython to check remote URLs
        repo = Repo(os.getcwd())
        for remote in repo.remotes:
            if any(repo_url in url for url in remote.urls):
                return {
                    "success": True,
                    "message": f"Repository {repo_url} is accessible",
                    "data": {"url": repo_url},
                }
        return {
            "success": False,
            "message": "Repository not found in remotes",
            "data": None,
        }
    except GitCommandError:
        return {
            "success": False,
            "message": "Failed to check repository access",
            "data": None,
        }


def check_for_conflicts() -> ToolOutput:
    """Check for merge conflicts in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        unmerged = repo.index.unmerged_blobs()
        conflicting_files = sorted(list(unmerged.keys()))
        if conflicting_files:
            log_key_value("Found conflicts in", ", ".join(conflicting_files))
        else:
            log_key_value("No conflicts found", "")
        return {
            "success": True,
            "message": "Conflicts found" if conflicting_files else "No conflicts found",
            "data": {
                "has_conflicts": bool(conflicting_files),
                "conflicting_files": conflicting_files,
            },
        }
    except GitCommandError as e:
        error_msg = f"Failed to check for conflicts: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def get_conflict_info() -> ToolOutput:
    """Get details about current conflicts from Git's index in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        conflicts = {}
        unmerged = repo.index.unmerged_blobs()

        for path, blobs in unmerged.items():
            log_key_value("Analyzing conflict in", path)
            versions = {}
            for stage, blob in blobs:
                if stage == 1:
                    versions["ancestor"] = blob.data_stream.read().decode()
                elif stage == 2:
                    versions["ours"] = blob.data_stream.read().decode()
                elif stage == 3:
                    versions["theirs"] = blob.data_stream.read().decode()
            conflicts[path] = {"content": versions}

        return {
            "success": True,
            "message": "Successfully retrieved conflict information",
            "data": {"conflicts": conflicts},
        }
    except GitCommandError as e:
        error_msg = f"Failed to get conflict info: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def resolve_conflict(file_path: str, resolution: str) -> ToolOutput:
    """Resolve a conflict in a specific file and commit the resolution in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        log_key_value("Resolving conflict in", file_path)
        full_path = Path(repo.working_dir) / file_path
        full_path.write_text(resolution)
        repo.git.add(file_path)
        return {
            "success": True,
            "message": f"Successfully resolved conflict in {file_path}",
            "data": {"file": file_path},
        }
    except GitCommandError as e:
        error_msg = f"Failed to resolve conflict: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }


def create_merge_commit(message: str) -> ToolOutput:
    """Create a merge commit after resolving conflicts in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        log_key_value("Creating merge commit", message)
        if check_for_conflicts()["has_conflicts"]:
            return {
                "success": False,
                "message": "Cannot create merge commit with unresolved conflicts",
                "data": None,
            }
        commit = repo.index.commit(message)
        return {
            "success": True,
            "message": f"Successfully created merge commit: {message}",
            "data": {"commit_id": commit.hexsha},
        }
    except GitCommandError as e:
        error_msg = f"Failed to create merge commit: {str(e)}"
        log_error(e, error_msg)
        return {
            "success": False,
            "message": error_msg,
            "data": None,
        }
