"""Module for Git operations."""

import os
import shutil
from pathlib import Path
from typing import Dict, Any
from git import Repo, GitCommandError
from src.utils.logging import log_key_value, log_error

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
) -> Dict[str, Any]:
    """
    Initialize a new Git repository.

    Args:
        path (str): Path where to initialize the repository
        user_name (str, optional): Git user name to configure
        user_email (str, optional): Git user email to configure

    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        log_key_value("Initializing repository at", path)
        repo = Repo.init(path)
        if user_name:
            repo.config_writer().set_value("user", "name", user_name).release()
        if user_email:
            repo.config_writer().set_value("user", "email", user_email).release()
        return {"success": True}
    except Exception as e:
        log_error(e, "Failed to initialize repository")
        return {"success": False, "error": str(e)}


def clone_repository(
    url: str, path: str, user_name: str = None, user_email: str = None
) -> Dict[str, Any]:
    """
    Clone a Git repository with proper path handling and cleanup.
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

        return {"success": True}
    except GitCommandError as e:
        error_msg = f"Clone failed with error: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def create_branch(branch_base: str) -> dict:
    """Create branch with automatic timestamp suffix"""
    try:
        # Validate base name
        if not branch_base:
            return {"success": False, "error": "Missing branch base name"}

        # Clean branch base name - remove special characters and spaces
        branch_base = branch_base.strip().lower()
        branch_base = "".join(
            c if c.isalnum() or c in "-_" else "-" for c in branch_base
        )
        if not branch_base:
            return {"success": False, "error": "Invalid branch name after cleaning"}

        # Generate branch name
        timestamp = int(time.time())
        branch_name = f"{branch_base}-{timestamp}"

        repo = Repo(os.getcwd())
        log_key_value("Creating branch", f"'{branch_name}' in {repo.working_dir}")

        # Check if we're in a git repo
        if not os.path.exists(os.path.join(repo.working_dir, ".git")):
            return {"success": False, "error": "Not a git repository"}

        # Check if we have a remote named 'origin'
        try:
            repo.remote("origin")
        except ValueError:
            return {"success": False, "error": "No 'origin' remote found"}

        # Create and checkout branch
        try:
            repo.git.checkout("-b", branch_name)
        except GitCommandError as e:
            if "already exists" in str(e):
                return {
                    "success": False,
                    "error": f"Branch '{branch_name}' already exists",
                }
            raise

        # Verify branch exists
        if branch_name not in repo.heads:
            return {
                "success": False,
                "error": f"Failed to create branch: {branch_name}",
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
            if "Permission denied" in str(e):
                return {
                    "success": False,
                    "error": "Permission denied pushing to remote",
                }
            elif "Authentication failed" in str(e):
                return {
                    "success": False,
                    "error": "Authentication failed - check your GitHub token",
                }
            else:
                raise

        return {
            "success": True,
            "branch_name": branch_name,
            "message": f"Created branch {branch_name}",
        }
    except GitCommandError as e:
        error_msg = f"Git error: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def checkout_branch(branch_name: str) -> Dict[str, Any]:
    """Check out an existing branch in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        log_key_value("Checking out branch", branch_name)
        branch = repo.heads[branch_name]
        branch.checkout()
        return {"success": True}
    except GitCommandError as e:
        error_msg = f"Failed to checkout branch: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def commit_and_push(message: str) -> Dict[str, Any]:
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
            "commit_hash": commit.hexsha,
            "message": f"Changes committed and pushed: {message}",
        }
    except GitCommandError as e:
        error_msg = f"Failed to commit and push: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def get_current_branch() -> Dict[str, Any]:
    """Get the current branch name in the working directory"""
    try:
        repo = Repo(os.getcwd())
        branch = repo.active_branch.name
        log_key_value("Current branch", branch)
        return {"success": True, "output": branch}
    except GitCommandError as e:
        error_msg = f"Failed to get current branch: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def list_branches() -> Dict[str, Any]:
    """List all branches in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        branches = [head.name for head in repo.heads]
        log_key_value("Branches", ", ".join(branches))
        return {"success": True, "output": branches}
    except GitCommandError as e:
        error_msg = f"Failed to list branches: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def add_remote(name: str, url: str) -> Dict[str, Any]:
    """Add a remote to the current repository."""
    try:
        repo_path = os.getcwd()
        # Insert GitHub token authentication logic
        repo = _get_repo(repo_path)
        log_key_value("Adding remote", f"{name} -> {url}")
        repo.create_remote(name, url)
        return {"success": True}
    except GitCommandError as e:
        error_msg = f"Failed to add remote: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def fetch_remote(remote_name: str) -> Dict[str, Any]:
    """Fetch from a remote in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        log_key_value("Fetching from remote", remote_name)
        remote = repo.remotes[remote_name]
        remote.fetch()
        return {"success": True}
    except GitCommandError as e:
        error_msg = f"Failed to fetch from remote: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def pull_remote(remote_name: str = "origin", branch: str = None) -> Dict[str, Any]:
    """Pull changes with explicit branch specification."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        branch = branch or repo.active_branch.name
        log_key_value("Pulling from remote", f"{remote_name}/{branch}")

        repo.git.pull(remote_name, branch, "--allow-unrelated-histories")

        # Check for conflicts after pull
        if check_for_conflicts()["has_conflicts"]:
            return {"success": False, "error": "Merge conflict detected after pull"}

        return {"success": True}
    except GitCommandError as e:
        error_msg = f"Failed to pull changes: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def can_access_repository(repo_url: str) -> Dict[str, Any]:
    """Check if a git repository is accessible."""
    try:
        log_key_value("Checking access to", repo_url)
        # Use GitPython to check remote URLs
        repo = Repo(os.getcwd())
        for remote in repo.remotes:
            if any(repo_url in url for url in remote.urls):
                return {"success": True}
        return {"success": False}
    except GitCommandError:
        return {"success": False}


def check_for_conflicts() -> Dict[str, Any]:
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
            "has_conflicts": bool(conflicting_files),
            "conflicting_files": conflicting_files,
        }
    except GitCommandError as e:
        error_msg = f"Failed to check for conflicts: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def get_conflict_info() -> Dict[str, Any]:
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

        return {"success": True, "conflicts": conflicts}
    except GitCommandError as e:
        error_msg = f"Failed to get conflict info: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def resolve_conflict(
    file_path: str, resolution: str, message: str = "Resolve conflict"
) -> Dict[str, Any]:
    """Resolve a conflict in a specific file and commit the resolution in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        log_key_value("Resolving conflict in", file_path)
        full_path = Path(repo.working_dir) / file_path
        full_path.write_text(resolution)
        repo.git.add(file_path)
        return {"success": True}
    except GitCommandError as e:
        error_msg = f"Failed to resolve conflict: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}


def create_merge_commit(message: str) -> Dict[str, Any]:
    """Create a merge commit after resolving conflicts in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        log_key_value("Creating merge commit", message)
        if check_for_conflicts()["has_conflicts"]:
            return {
                "success": False,
                "error": "Cannot create merge commit with unresolved conflicts",
            }
        commit = repo.index.commit(message)
        return {"success": True, "commit_id": commit.hexsha}
    except GitCommandError as e:
        error_msg = f"Failed to create merge commit: {str(e)}"
        log_error(e, error_msg)
        return {"success": False, "error": error_msg}
