"""Module for GitHub operations."""

import os
from typing import Dict, Any, List
from github import Github, Auth, GithubException
from dotenv import load_dotenv
import ast
from src.tools.git_operations import (
    fetch_remote,
    pull_remote,
)
from src.utils.logging import log_key_value, log_error

import time
from git import Repo, GitCommandError
from src.task.constants import PR_TEMPLATE, REVIEW_TEMPLATE

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


def fork_repository(repo_full_name: str, repo_path: str = None) -> dict:
    """
    Fork a repository and clone it locally.

    Args:
        repo_full_name: Full name of repository (owner/repo)
        repo_path: Local path to clone to

    Returns:
        dict: Result with success status and error message if any
    """
    try:
        gh = _get_github_client()
        original_repo = gh.get_repo(repo_full_name)

        # Check if we already have a fork
        user = gh.get_user()
        try:
            fork = user.get_repo(repo_full_name.split("/")[1])
            if fork.fork and fork.parent.full_name == repo_full_name:
                log_key_value("Using existing fork of", repo_full_name)
            else:
                log_key_value("Creating new fork of", repo_full_name)
                fork = original_repo.create_fork()
        except GithubException:
            log_key_value("Creating new fork of", repo_full_name)
            fork = original_repo.create_fork()

        # Wait for fork to be ready
        log_key_value("Waiting for fork to be ready", "")
        time.sleep(5)  # Give GitHub time to complete the fork

        # Clone fork if path provided
        if repo_path:
            log_key_value("Cloning to", repo_path)
            # Add GitHub token authentication
            if "github.com" in fork.clone_url:
                token = os.environ["GITHUB_TOKEN"]
                clone_url = fork.clone_url.replace("https://", f"https://{token}@")
                log_key_value("Using clone URL", clone_url)

                repo = Repo.clone_from(clone_url, repo_path)

                # Set up remotes
                log_key_value("Configuring remotes", "")
                log_key_value("origin", fork.html_url)
                log_key_value("upstream", original_repo.html_url)

                # Configure remotes - origin is already set by clone_from
                upstream_url = original_repo.clone_url.replace(
                    "https://", f"https://{token}@"
                )
                repo.create_remote("upstream", upstream_url)

                # Configure Git user info
                with repo.config_writer() as config:
                    config.set_value("user", "name", os.environ["GITHUB_USERNAME"])
                    config.set_value(
                        "user",
                        "email",
                        f"{os.environ['GITHUB_USERNAME']}@users.noreply.github.com",
                    )

                return {"success": True, "fork": fork, "repo": repo}
        return {"success": True, "fork": fork}

    except Exception as e:
        error_msg = f"Failed to fork/clone repository: {str(e)}"
        log_error(e, error_msg)
        if "permission" in str(e).lower():
            log_key_value("This appears to be a permissions issue. Please check", "")
            log_key_value("1.", "Your GitHub token has 'repo' scope")
            log_key_value("2.", "You have access to the repository")
            log_key_value("3.", "The repository name is correct")
        return {"success": False, "error": error_msg}


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

        # Auto-format head branch if needed
        if ":" not in head:
            head = f"{os.environ['GITHUB_USERNAME']}:{head}"

        # Ensure base branch is just the name without owner
        base = base.split(":")[-1]  # Remove owner prefix if present

        # Format tests into markdown bullets
        tests_bullets = " - " + "\n - ".join(ast.literal_eval(tests))

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
    except GithubException as e:
        return {
            "success": False,
            "error": f"GitHub API error: {e.data.get('message', str(e))}",
            "details": e.data.get("errors", []),
        }
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}", "details": []}


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
        try:
            repo = Repo(repo_path)
            # First try normal push
            try:
                repo.git.push("origin", branch)
            except GitCommandError:
                # If failed, pull and try again
                repo.git.pull("origin", branch)
                repo.git.push("origin", branch)
        except GitCommandError as e:
            error_msg = f"Failed to push changes: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}

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


def review_pull_request(
    repo_full_name: str,
    pr_number: int,
    title: str,
    summary: str,
    requirements: Dict[str, List[str]],
    test_evaluation: Dict[str, List[str]],
    recommendation: str,
    recommendation_reason: List[str],
    action_items: List[str],
) -> Dict[str, Any]:
    """
    Post a structured review comment on a pull request.

    Args:
        repo_full_name (str): Full name of the repository (owner/repo)
        pr_number (int): Pull request number
        title (str): Title of the PR
        summary (str): Summary of the changes
        requirements (Dict[str, List[str]]): Dictionary with 'met' and 'not_met' requirements
        test_evaluation (Dict[str, List[str]]): Dictionary with test evaluation details
        recommendation (str): APPROVE/REVISE/REJECT
        recommendation_reason (List[str]): List of reasons for the recommendation
        action_items (List[str]): List of required changes or improvements

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation succeeded
            - error (str): Error message if unsuccessful
    """
    try:
        gh = _get_github_client()
        repo = gh.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        # Format lists into markdown bullet points
        def format_list(items: List[str], empty_message: str = "None") -> str:
            if not items:
                return f"*{empty_message}*"
            return "- " + "\n- ".join(items)

        # Format the review using the template
        review_body = REVIEW_TEMPLATE.format(
            title=title,
            summary=summary,
            met_requirements=format_list(
                requirements.get("met", []), "All requirements need work"
            ),
            unmet_requirements=format_list(
                requirements.get("not_met", []), "All requirements are met"
            ),
            test_coverage=format_list(
                test_evaluation.get("coverage", []), "No adequate test coverage found"
            ),
            test_issues=format_list(
                test_evaluation.get("issues", []), "No issues found in existing tests"
            ),
            missing_tests=format_list(
                test_evaluation.get("missing", []), "No missing test cases identified"
            ),
            recommendation=recommendation,
            recommendation_reasons=format_list(
                recommendation_reason, "No specific reasons provided"
            ),
            action_items=format_list(action_items, "No action items required"),
        )

        # Post the review
        pr.create_issue_comment(review_body)
        validated = recommendation == "APPROVE"
        return {"success": True, "validated": validated}
    except Exception as e:
        error_msg = f"Error posting review on PR #{pr_number}: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
