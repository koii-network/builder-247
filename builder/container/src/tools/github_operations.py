"""Module for GitHub operations."""

import os

from typing import Dict, Any
from github import Github, Auth, GithubException
from dotenv import load_dotenv
from src.tools.git_operations import (
    fetch_remote,
    pull_remote,
    push_remote,
)

import time
from git import Repo
from src.task.constants import PR_TEMPLATE

# Load environment variables from .env file
load_dotenv()


def _get_github_client() -> Github:
    """
    Get an authenticated GitHub client.

    Returns:
        Github: Authenticated GitHub client

    Raises:
        ValueError: If GITHUB_TOKEN is not set
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("Missing GITHUB_TOKEN")
    return Github(auth=Auth.Token(token))


def fork_repository(repo_full_name: str, repo_path: str) -> dict:
    """Forks a repository and configures proper remotes"""
    try:
        gh = _get_github_client()

        # Create fork using GitHub API
        print(f"Forking repository: {repo_full_name}")
        original_repo = gh.get_repo(repo_full_name)
        fork = gh.get_user().create_fork(original_repo)

        # Wait for fork propagation
        print("Waiting for fork to be ready...")
        time.sleep(5)

        # Clone the fork with authentication
        print(f"Cloning to {repo_path}")
        authenticated_url = (
            f"https://{os.environ['GITHUB_TOKEN']}@github.com/{fork.full_name}.git"
        )
        repo = Repo.clone_from(authenticated_url, repo_path)

        # Configure remotes
        print("Configuring remotes:")
        print(f"origin -> {fork.clone_url}")
        print(f"upstream -> {original_repo.clone_url}")

        # Set push URL for origin to include token
        with repo.config_writer() as config:
            config.set_value('remote "origin"', "url", authenticated_url)

        # Add upstream remote
        repo.create_remote("upstream", original_repo.clone_url)

        # Set default push/pull behavior
        with repo.config_writer() as config:
            config.set_value("push", "default", "current")

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_pull_request(
    repo_full_name: str,
    title: str,
    head: str,
    summary: str,
    tests: str,
    todo: str,
    acceptance_criteria: str,
    base: str = "main",
) -> Dict[str, Any]:
    """Create PR with formatted description"""
    try:
        gh = _get_github_client()
        # Format tests into markdown bullets
        tests_bullets = "\n".join([f"- {t.strip()}" for t in tests.split("\n")])

        body = PR_TEMPLATE.format(
            todo=todo,
            title=title,
            acceptance_criteria=acceptance_criteria,
            summary=summary,
            tests=tests_bullets,
        )

        repo = gh.get_repo(repo_full_name)
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return {"success": True, "pr_url": pr.html_url}
    except Exception as e:
        return {"success": False, "error": str(e)}


def sync_fork(repo_path: str, branch: str = "main") -> Dict[str, Any]:
    """
    Sync a fork with its upstream repository.

    Args:
        repo_path (str): Path to the git repository
        branch (str): Branch to sync (default: main)

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - error (str): Error message if unsuccessful
    """
    try:
        print(f"Syncing fork with upstream, branch: {branch}")

        # Fetch from upstream
        fetch_result = fetch_remote(repo_path, "upstream")
        if not fetch_result["success"]:
            return fetch_result

        # Pull from upstream
        pull_result = pull_remote(repo_path, "upstream", branch)
        if not pull_result["success"]:
            return pull_result

        # Push to origin
        push_result = push_remote(repo_path, "origin", branch)
        if not push_result["success"]:
            return push_result

        print("Successfully synced fork with upstream")
        return {"success": True}
    except Exception as e:
        error_msg = f"Unexpected error while syncing fork: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}


def check_fork_exists(owner: str, repo_name: str) -> Dict[str, Any]:
    """
    Check if fork exists using GitHub API.

    Args:
        owner (str): Owner of the repository
        repo_name (str): Name of the repository

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - exists (bool): Whether the fork exists
            - error (str): Error message if unsuccessful
    """
    try:
        gh = _get_github_client()

        # First check if the source repo exists
        try:
            gh.get_repo(f"{owner}/{repo_name}")
        except GithubException:
            return {"success": False, "error": "Source repository not found"}

        # Then check if we have a fork
        user = gh.get_user()
        try:
            fork = user.get_repo(repo_name)
            # Verify it's actually a fork of the target repo
            if fork.fork and fork.parent.full_name == f"{owner}/{repo_name}":
                return {"success": True, "exists": True}
            return {"success": True, "exists": False}
        except GithubException:
            return {"success": True, "exists": False}

    except Exception as e:
        return {"success": False, "error": str(e)}
