"""Module for Git operations."""

import os
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from git import Repo, GitCommandError
from src.tools.execute_command import execute_command


def run_git_command(repo: Repo, command: str, **kwargs) -> Dict[str, Any]:
    """
    Run a Git command using GitPython and return the result.

    Args:
        repo (Repo): The GitPython Repo instance
        command (str): The Git command to run
        **kwargs: Additional arguments to pass to the git command

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - output (str): Command output if successful
            - error (str): Error message if unsuccessful
    """
    try:
        git = repo.git
        method = getattr(git, command.replace("-", "_"))
        output = method(**kwargs)
        return {"success": True, "output": output}
    except GitCommandError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
        return {"success": True, "repo": repo}
    except Exception as e:
        return {"success": False, "error": str(e)}


def clone_repository(
    url: str, path: str, user_name: str = None, user_email: str = None
) -> Dict[str, Any]:
    """
    Clone a Git repository.

    Args:
        url (str): URL of the repository to clone
        path (str): Path where to clone the repository
        user_name (str, optional): Git user name to configure
        user_email (str, optional): Git user email to configure

    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        repo = Repo.clone_from(url, path)
        if user_name:
            repo.config_writer().set_value("user", "name", user_name).release()
        if user_email:
            repo.config_writer().set_value("user", "email", user_email).release()
        return {"success": True, "repo": repo}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_branch(repo: Repo, branch_name: str) -> Dict[str, Any]:
    """
    Create a new Git branch.

    Args:
        repo (Repo): The GitPython Repo instance
        branch_name (str): Name of the branch to create

    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        current = repo.active_branch
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()
        return {"success": True, "previous_branch": current.name}
    except Exception as e:
        return {"success": False, "error": str(e)}


def checkout_branch(repo: Repo, branch_name: str) -> Dict[str, Any]:
    """
    Check out an existing Git branch.

    Args:
        repo (Repo): The GitPython Repo instance
        branch_name (str): Name of the branch to check out

    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        branch = repo.heads[branch_name]
        branch.checkout()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def make_commit(repo: Repo, message: str, add_all: bool = True) -> Dict[str, Any]:
    """
    Stage changes and create a commit.

    Args:
        repo (Repo): The GitPython Repo instance
        message (str): The commit message
        add_all (bool): Whether to stage all changes

    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        if add_all:
            repo.git.add(A=True)
        else:
            repo.git.add(u=True)
        commit = repo.index.commit(message)
        return {"success": True, "commit_hash": commit.hexsha}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_current_branch(repo: Repo) -> Dict[str, Any]:
    """
    Get the name of the current Git branch.

    Args:
        repo (Repo): The GitPython Repo instance

    Returns:
        Dict[str, Any]: Result of the operation with the branch name in the 'output' field
    """
    try:
        return {"success": True, "output": repo.active_branch.name}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_branches(repo: Repo) -> Dict[str, Any]:
    """
    List all Git branches.

    Args:
        repo (Repo): The GitPython Repo instance

    Returns:
        Dict[str, Any]: Result of the operation with branch list in the 'output' field
    """
    try:
        branches = [head.name for head in repo.heads]
        return {"success": True, "output": branches}
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_remote(repo: Repo, name: str, url: str) -> Dict[str, Any]:
    """
    Add a remote to the repository.

    Args:
        repo (Repo): The GitPython Repo instance
        name (str): Name of the remote
        url (str): URL of the remote

    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        repo.create_remote(name, url)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def fetch_remote(repo: Repo, remote_name: str = "origin") -> Dict[str, Any]:
    """
    Fetch from a remote.

    Args:
        repo (Repo): The GitPython Repo instance
        remote_name (str): Name of the remote to fetch from

    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        remote = repo.remotes[remote_name]
        remote.fetch()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def pull_remote(
    repo: Repo, remote_name: str = "origin", branch: str = None
) -> Dict[str, Any]:
    """
    Pull from a remote.

    Args:
        repo (Repo): The GitPython Repo instance
        remote_name (str): Name of the remote to pull from
        branch (str, optional): Branch to pull. If None, pulls active branch

    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        remote = repo.remotes[remote_name]
        if branch:
            remote.pull(branch)
        else:
            remote.pull()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def push_remote(
    repo: Repo, remote_name: str = "origin", branch: str = None
) -> Dict[str, Any]:
    """
    Push to a remote.

    Args:
        repo (Repo): The GitPython Repo instance
        remote_name (str): Name of the remote to push to
        branch (str, optional): Branch to push. If None, pushes active branch

    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        # Get the remote
        remote = repo.remotes[remote_name]

        # Get the current URL
        url = remote.url

        # If using HTTPS and token is in the environment, add it to URL
        token = os.environ.get("GITHUB_TOKEN")
        if token and url.startswith("https://"):
            new_url = url.replace("https://", f"https://{token}@")
            remote.set_url(new_url)

        try:
            # Do the push
            if branch:
                remote.push(branch)
            else:
                remote.push()
            return {"success": True}
        finally:
            # Restore original URL if we changed it
            if token and url.startswith("https://"):
                remote.set_url(url)

    except Exception as e:
        return {"success": False, "error": str(e)}


def can_access_repository(repo_url: str) -> bool:
    """Check if a git repository is accessible."""
    try:
        # Ensure we're using HTTPS and disable credential prompting
        https_url = repo_url.replace("git@github.com:", "https://github.com/").replace(
            "ssh://git@github.com/", "https://github.com/"
        )
        if not https_url.startswith("https://"):
            https_url = (
                f"https://github.com/{https_url}"
                if "/" in https_url
                else f"https://github.com//{https_url}"
            )

        result = execute_command(f"GIT_TERMINAL_PROMPT=0 git ls-remote {https_url}")
        return result[2] == 0  # Check return code
    except (OSError, subprocess.SubprocessError):
        return False


def check_fork_exists(owner: str, repo_name: str) -> Dict[str, Any]:
    """Check if fork exists using GitHub API."""
    try:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo_name}",
            headers={"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"},
        )
        if response.status_code != 200:
            return {"success": False, "error": "Repository not found"}
        return {"success": True, "exists": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def commit_and_push(
    repo: Repo, message: str, file_path: Optional[str] = None
) -> Dict[str, Any]:
    """Commit and push changes."""
    try:
        if file_path:
            repo.git.add(file_path)
        else:
            repo.git.add(A=True)
        repo.index.commit(message)
        origin = repo.remotes.origin
        repo.git.push(origin)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_for_conflicts(repo: Repo) -> Dict[str, Any]:
    """Check if there are merge conflicts."""
    try:
        # Check unmerged paths in the index
        unmerged = repo.index.unmerged_blobs()
        conflicting_files = list(unmerged.keys())

        # If no unmerged blobs found, check for conflict markers in files
        if not conflicting_files:
            for file_path in repo.git.ls_files().split("\n"):
                if not file_path:
                    continue
                try:
                    with open(Path(repo.working_dir) / file_path) as f:
                        content = f.read()
                        if "<<<<<<< HEAD" in content:
                            conflicting_files.append(file_path)
                except (IOError, OSError):
                    continue

        return {
            "success": True,
            "has_conflicts": bool(conflicting_files),
            "conflicting_files": conflicting_files,
        }
    except (GitCommandError, IOError, OSError) as e:
        return {"success": False, "error": str(e)}


def get_conflict_info(repo: Repo) -> Dict[str, Any]:
    """Get details about current conflicts."""
    try:
        conflicts = {}
        unmerged = repo.index.unmerged_blobs()

        # First try to get info from unmerged blobs
        for path, blobs in unmerged.items():
            versions = {}
            for stage_blob in blobs:
                stage = stage_blob.stage
                blob = stage_blob.blob
                if stage == 1:
                    versions["ancestor"] = blob.data_stream.read().decode()
                elif stage == 2:
                    versions["ours"] = blob.data_stream.read().decode()
                elif stage == 3:
                    versions["theirs"] = blob.data_stream.read().decode()
            conflicts[path] = {"content": versions}

        # If no unmerged blobs, check for conflict markers
        if not conflicts:
            for file_path in repo.git.ls_files().split("\n"):
                if not file_path:
                    continue
                try:
                    with open(Path(repo.working_dir) / file_path) as f:
                        content = f.read()
                        if "<<<<<<< HEAD" in content:
                            conflicts[file_path] = {"content": {"raw": content}}
                except (IOError, OSError):
                    continue

        return {"success": True, "conflicts": conflicts}
    except (GitCommandError, IOError, OSError) as e:
        return {"success": False, "error": str(e)}


def resolve_conflict(
    repo: Repo, file_path: str, resolution: str, message: str = "Resolve conflict"
) -> Dict[str, Any]:
    """Resolve a conflict in a specific file and commit the resolution."""
    try:
        # Write the resolved content
        full_path = Path(repo.working_dir) / file_path
        full_path.write_text(resolution)

        # Stage the resolved file
        repo.index.add([file_path])

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_merge_commit(repo: Repo, message: str) -> Dict[str, Any]:
    """Create a merge commit after resolving conflicts."""
    try:
        # Check if there are any remaining conflicts
        if check_for_conflicts(repo)["has_conflicts"]:
            return {
                "success": False,
                "error": "Cannot create merge commit with unresolved conflicts",
            }

        # Create the merge commit
        commit = repo.index.commit(message)
        return {"success": True, "commit_id": commit.hexsha}
    except Exception as e:
        return {"success": False, "error": str(e)}
