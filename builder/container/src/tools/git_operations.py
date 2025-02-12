"""Module for Git operations."""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from git import Repo
from src.tools.execute_command import execute_command


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
        repo = Repo.init(path)
        if user_name:
            repo.config_writer().set_value("user", "name", user_name).release()
        if user_email:
            repo.config_writer().set_value("user", "email", user_email).release()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def clone_repository(
    url: str, path: str, user_name: str = None, user_email: str = None
) -> Dict[str, Any]:
    """
    Clone a Git repository with proper path handling and cleanup.
    """
    try:
        print(f"Attempting to clone repository to: {os.path.abspath(path)}")
        print(f"Source URL: {url}")

        # Clean up existing path if it exists
        if os.path.exists(path):
            print(f"Removing existing path: {path}")
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

        # Create target directory
        print(f"Creating directory: {path}")
        os.makedirs(path, exist_ok=True)

        # Add GitHub token authentication
        token = os.environ.get("GITHUB_TOKEN")
        if token and "github.com" in url:
            print("Adding GitHub token authentication to URL")
            if url.startswith("https://"):
                url = url.replace("https://", f"https://{token}@")
            elif url.startswith("git@"):
                url = f"https://{token}@github.com/{url.split(':', 1)[1]}"
            print(f"Modified URL: {url}")

        # Clone repository
        print("Starting clone operation...")
        repo = Repo.clone_from(url, path)
        print("Clone completed successfully")

        # Configure user information
        if user_name or user_email:
            print(f"Configuring user: {user_name} <{user_email}>")
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
    except Exception as e:
        print(f"Clone failed with error: {str(e)}")
        return {"success": False, "error": str(e)}


def create_branch(branch_name: str) -> dict:
    """Create branch in current working directory"""
    try:
        repo = Repo(os.getcwd())  # Now uses the flow-managed directory
        print(f"Creating branch '{branch_name}' in {repo.working_dir}")

        # Create and checkout branch
        repo.git.checkout("-b", branch_name)

        # Verify branch exists
        if branch_name not in repo.heads:
            raise Exception(f"Branch creation failed: {branch_name}")

        # Configure upstream tracking
        repo.git.push("--set-upstream", "origin", branch_name)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def checkout_branch(branch_name: str) -> Dict[str, Any]:
    """Check out an existing branch in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        branch = repo.heads[branch_name]
        branch.checkout()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def make_commit(message: str, add_all: bool = True) -> Dict[str, Any]:
    """Stage changes and create a commit in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        if add_all:
            repo.git.add(A=True)
        else:
            repo.git.add(u=True)
        commit = repo.index.commit(message)
        return {"success": True, "commit_hash": commit.hexsha}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_current_branch() -> Dict[str, Any]:
    """Get the current branch name in the working directory"""
    try:
        repo = Repo(os.getcwd())
        return {"success": True, "output": repo.active_branch.name}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_branches() -> Dict[str, Any]:
    """List all branches in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        branches = [head.name for head in repo.heads]
        return {"success": True, "output": branches}
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_remote(name: str, url: str) -> Dict[str, Any]:
    """Add a remote to the current repository."""
    try:
        repo_path = os.getcwd()
        # Insert GitHub token authentication logic
        repo = _get_repo(repo_path)
        repo.create_remote(name, url)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def fetch_remote(remote_name: str) -> Dict[str, Any]:
    """Fetch from a remote in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        remote = repo.remotes[remote_name]
        remote.fetch()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def pull_remote(remote_name: str = "origin", branch: str = None) -> Dict[str, Any]:
    """Pull changes with explicit branch specification."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        branch = branch or repo.active_branch.name

        repo.git.pull(remote_name, branch, "--allow-unrelated-histories")

        # Check for conflicts after pull
        if check_for_conflicts()["has_conflicts"]:
            return {"success": False, "error": "Merge conflict detected after pull"}

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def push_remote(remote_name: str = "origin", branch: str = None) -> Dict[str, Any]:
    """Push changes with automatic conflict resolution."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        current_branch = repo.active_branch.name
        branch = branch or current_branch

        # First try normal push
        try:
            repo.git.push(remote_name, branch)
            return {"success": True}
        except Exception as e:
            # If failed, pull and try again
            repo.git.pull(remote_name, branch)
            repo.git.push(remote_name, branch)
            return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def can_access_repository(repo_url: str) -> bool:
    """Check if a git repository is accessible."""
    try:
        # Use GitPython to check remote URLs
        repo = Repo(os.getcwd())
        for remote in repo.remotes:
            if any(repo_url in url for url in remote.urls):
                return True
        return False
    except Exception as e:
        return False


def commit_and_push(message: str) -> Dict[str, Any]:
    """Commit and push changes in the current working directory"""
    try:
        repo = Repo(os.getcwd())
        repo.git.add(A=True)
        repo.index.commit(message)
        repo.git.push("origin", repo.active_branch.name)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_for_conflicts() -> Dict[str, Any]:
    """Check for merge conflicts in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        unmerged = repo.index.unmerged_blobs()
        conflicting_files = sorted(list(unmerged.keys()))
        return {
            "success": True,
            "has_conflicts": bool(conflicting_files),
            "conflicting_files": conflicting_files,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_conflict_info() -> Dict[str, Any]:
    """Get details about current conflicts from Git's index in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        conflicts = {}
        unmerged = repo.index.unmerged_blobs()

        for path, blobs in unmerged.items():
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
    except Exception as e:
        return {"success": False, "error": str(e)}


def resolve_conflict(
    file_path: str, resolution: str, message: str = "Resolve conflict"
) -> Dict[str, Any]:
    """Resolve a conflict in a specific file and commit the resolution in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        full_path = Path(repo.working_dir) / file_path
        full_path.write_text(resolution)
        repo.git.add(file_path)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_merge_commit(message: str) -> Dict[str, Any]:
    """Create a merge commit after resolving conflicts in the current repository."""
    try:
        repo_path = os.getcwd()
        repo = _get_repo(repo_path)
        if check_for_conflicts()["has_conflicts"]:
            return {
                "success": False,
                "error": "Cannot create merge commit with unresolved conflicts",
            }
        commit = repo.index.commit(message)
        return {"success": True, "commit_id": commit.hexsha}
    except Exception as e:
        return {"success": False, "error": str(e)}
