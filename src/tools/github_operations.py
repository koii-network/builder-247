"""Module for GitHub operations."""

import os
from pathlib import Path
from typing import Dict, Any
from github import Github, Auth, GithubException
from dotenv import load_dotenv
from .pr_template import validate_pr_description
from src.tools.git_operations import (
    clone_repository,
    add_remote,
    fetch_remote,
    pull_remote,
    push_remote,
)

import time

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


def _get_github_username() -> str:
    """
    Get the GitHub username from environment.

    Returns:
        str: GitHub username

    Raises:
        ValueError: If GITHUB_USERNAME is not set
    """
    username = os.environ.get("GITHUB_USERNAME")
    if not username:
        raise ValueError("Missing GITHUB_USERNAME")
    return username


def get_pr_template(repo_path: str) -> Dict[str, Any]:
    """
    Get the PR template content from the repository's .github directory.

    Args:
        repo_path (str): Path to the git repository

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - template (str): The template content if successful
            - error (str): Error message if unsuccessful
    """
    try:
        template_path = Path(repo_path) / ".github" / "pull_request_template.md"

        if not template_path.exists():
            return {"success": False, "error": "No PR template found"}

        # Read and return the template content
        content = template_path.read_text()
        return {"success": True, "template": content}
    except Exception as e:
        return {"success": False, "error": str(e)}


def fork_repository(repo_full_name: str, local_path: str = None) -> Dict[str, Any]:
    """
    Fork a repository and clone it locally.

    Args:
        repo_full_name (str): Full name of the repository (e.g. "owner/repo")
        local_path (str, optional): Directory where to clone the fork.
                                  If None, uses current directory

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - fork_url (str): URL of the forked repository if successful
            - fork_full_name (str): Full name of the fork if successful
            - error (str): Error message if unsuccessful
    """
    try:
        gh = _get_github_client()
        username = _get_github_username()

        print(f"Getting repository: {repo_full_name}")
        repo = gh.get_repo(repo_full_name)
        print(f"Creating fork of repository: {repo.full_name}")
        fork = gh.get_user().create_fork(repo)
        print(f"Fork created: {fork.full_name}")
        print(f"Fork URL: {fork.clone_url}")

        # Wait for GitHub to propagate the fork
        print("Waiting for fork to be propagated...")
        time.sleep(5)

        # Clone the fork
        target_dir = local_path or os.path.basename(fork.name)
        print(f"Cloning fork to {target_dir}")
        clone_result = clone_repository(
            fork.clone_url,
            target_dir,
            user_name=username,
            user_email=f"{username}@users.noreply.github.com",
        )

        if not clone_result["success"]:
            print(f"Failed to clone repository: {clone_result['error']}")
            return {
                "success": False,
                "error": f"Failed to clone repository: {clone_result['error']}",
            }

        # Add upstream remote
        upstream_url = f"https://github.com/{repo_full_name}.git"
        print(f"Adding upstream remote: {upstream_url}")
        add_remote_result = add_remote(target_dir, "upstream", upstream_url)
        if not add_remote_result["success"]:
            print(f"Failed to add upstream remote: {add_remote_result['error']}")
            return {
                "success": False,
                "error": f"Failed to add upstream remote: {add_remote_result['error']}",
            }

        return {
            "success": True,
            "fork_url": fork.clone_url,
            "fork_full_name": fork.full_name,
            "repo_path": target_dir,
        }
    except GithubException as e:
        print(f"GitHub API error: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def create_pull_request(
    repo_full_name: str,
    title: str,
    body: str,
    head: str,
    base: str = "main",
    validate_template: bool = True,
) -> Dict[str, Any]:
    """
    Create a pull request.

    Args:
        repo_full_name (str): Full name of the repository (e.g. "owner/repo")
        title (str): Title of the pull request
        body (str): Description/body of the pull request
        head (str): The name of the branch where your changes are implemented
        base (str): The name of the branch you want your changes pulled into
        validate_template (bool): Whether to validate the PR description against the template

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - pr_url (str): URL of the pull request if successful
            - error (str): Error message if unsuccessful
            - template_errors (list): List of template validation errors if any
    """
    try:
        if validate_template:
            print("Validating PR description against template...")
            validation = validate_pr_description(body)
            if not validation["valid"]:
                print(
                    f"PR description validation failed with errors: {validation['errors']}"
                )
                return {
                    "success": False,
                    "error": "PR description does not match template",
                    "template_errors": validation["errors"],
                }
            print("PR description validation passed")

        gh = _get_github_client()
        print(f"Getting repository: {repo_full_name}")
        repo = gh.get_repo(repo_full_name)
        print(f"Creating pull request in repository: {repo.full_name}")
        print(f"PR details: title='{title}', head='{head}', base='{base}'")
        pr = repo.create_pull(
            title=title,
            body=body,
            head=head,
            base=base,
        )
        print(f"Pull request created: {pr.html_url}")
        return {"success": True, "pr_url": pr.html_url}
    except GithubException as e:
        print(f"GitHub API error: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


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
