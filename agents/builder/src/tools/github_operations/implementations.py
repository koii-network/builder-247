"""Module for GitHub operations."""

import os
from typing import Dict, List
from github import Github, Auth, GithubException
from dotenv import load_dotenv
from src.tools.git_operations.implementations import (
    fetch_remote,
    pull_remote,
)
from src.utils.logging import log_key_value, log_error
from src.types import ToolOutput

import time
from git import Repo, GitCommandError
from src.workflows.prompts import PR_TEMPLATE, REVIEW_TEMPLATE

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


def fork_repository(repo_full_name: str, repo_path: str = None) -> ToolOutput:
    """
    Fork a repository and clone it locally.

    Args:
        repo_full_name: Full name of repository (owner/repo)
        repo_path: Local path to clone to

    Returns:
        ToolOutput: Standardized tool output with success status and error message if any
    """
    try:
        gh = _get_github_client()
        original_repo = gh.get_repo(repo_full_name)

        # Get authenticated user
        user = gh.get_user()
        username = user.login

        # Check if fork already exists
        try:
            fork = gh.get_repo(f"{username}/{original_repo.name}")
            log_key_value("Using existing fork of", repo_full_name)
        except GithubException:
            # Create fork if it doesn't exist
            fork = user.create_fork(original_repo)
            log_key_value("Created new fork of", repo_full_name)

        # Wait for fork to be ready
        log_key_value("Waiting for fork to be ready", "")
        max_retries = 10
        for _ in range(max_retries):
            try:
                fork.get_commits().get_page(0)
                break
            except GithubException:
                time.sleep(1)

        # Clone repository if path provided
        if repo_path:
            log_key_value("Cloning to", repo_path)
            # Use token for auth
            token = os.environ["GITHUB_TOKEN"]
            clone_url = (
                f"https://{token}@github.com/{username}/{original_repo.name}.git"
            )
            log_key_value("Using clone URL", clone_url)

            # Clone the repository
            repo = Repo.clone_from(clone_url, repo_path)

            # Configure remotes
            log_key_value("Configuring remotes", "")
            origin = repo.remote("origin")
            origin.set_url(f"https://github.com/{username}/{original_repo.name}")
            log_key_value(
                "origin", f"https://github.com/{username}/{original_repo.name}"
            )

            # Create and configure upstream remote
            repo.create_remote("upstream", f"https://github.com/{repo_full_name}")
            log_key_value("upstream", f"https://github.com/{repo_full_name}")

            # Fetch from upstream
            fetch_remote(repo_path, "upstream")

        return {
            "success": True,
            "message": f"Successfully forked and cloned {repo_full_name}",
            "data": {
                "fork_url": fork.html_url,
                "clone_path": repo_path,
                "owner": username,
                "repo": original_repo.name,
            },
            "error": None,
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


def create_pull_request(
    repo_full_name: str,
    title: str,
    head: str,
    description: str,
    tests: List[str],
    todo: str,
    acceptance_criteria: str,
    base: str = "main",
) -> ToolOutput:
    """Create PR with formatted description.

    Args:
        repo_full_name: Full name of repository (owner/repo)
        title: PR title
        head: Head branch name
        description: PR description
        tests: List of test descriptions
        todo: Original todo task
        acceptance_criteria: Task acceptance criteria
        base: Base branch name (default: main)

    Returns:
        ToolOutput: Standardized tool output with PR URL on success
    """
    try:
        gh = _get_github_client()

        # Auto-format head branch if needed
        if ":" not in head:
            head = f"{os.environ['GITHUB_USERNAME']}:{head}"

        # Ensure base branch is just the name without owner
        base = base.split(":")[-1]  # Remove owner prefix if present

        # Format tests into markdown bullets
        tests_bullets = " - " + "\n - ".join(tests)

        body = PR_TEMPLATE.format(
            todo=todo,
            title=title,
            acceptance_criteria=acceptance_criteria,
            description=description,
            tests=tests_bullets,
        )

        repo = gh.get_repo(repo_full_name)
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return {
            "success": True,
            "message": f"Successfully created PR: {title}",
            "data": {"pr_url": pr.html_url},
            "error": None,
        }
    except GithubException as e:
        return {
            "success": False,
            "message": "Failed to create pull request",
            "data": {"errors": e.data.get("errors", [])},
            "error": f"GitHub API error: {e.data.get('message', str(e))}",
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to create pull request",
            "data": None,
            "error": f"Unexpected error: {str(e)}",
        }


def sync_fork(repo_path: str, branch: str = "main") -> ToolOutput:
    """
    Sync a fork with its upstream repository.

    Args:
        repo_path: Path to the git repository
        branch: Branch to sync (default: main)

    Returns:
        ToolOutput: Standardized tool output with sync status
    """
    try:
        print(f"Syncing fork with upstream, branch: {branch}")

        # Fetch from upstream
        fetch_result = fetch_remote(repo_path, "upstream")
        if not fetch_result["success"]:
            return {
                "success": False,
                "message": "Failed to fetch from upstream",
                "data": None,
                "error": fetch_result.get("error"),
            }

        # Pull from upstream
        pull_result = pull_remote(repo_path, "upstream", branch)
        if not pull_result["success"]:
            return {
                "success": False,
                "message": "Failed to pull from upstream",
                "data": None,
                "error": pull_result.get("error"),
            }

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
            return {
                "success": False,
                "message": "Failed to push to origin",
                "data": None,
                "error": error_msg,
            }

        print("Successfully synced fork with upstream")
        return {
            "success": True,
            "message": f"Successfully synced branch {branch} with upstream",
            "data": {"branch": branch},
            "error": None,
        }
    except Exception as e:
        error_msg = f"Unexpected error while syncing fork: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": "Failed to sync fork",
            "data": None,
            "error": error_msg,
        }


def check_fork_exists(owner: str, repo_name: str) -> ToolOutput:
    """
    Check if fork exists using GitHub API.

    Args:
        owner: Owner of the repository
        repo_name: Name of the repository

    Returns:
        ToolOutput: Standardized tool output with fork existence status
    """
    try:
        gh = _get_github_client()

        # First check if the source repo exists
        try:
            gh.get_repo(f"{owner}/{repo_name}")
        except GithubException:
            return {
                "success": False,
                "message": "Source repository not found",
                "data": None,
                "error": "Source repository not found",
            }

        # Then check if we have a fork
        user = gh.get_user()
        try:
            fork = user.get_repo(repo_name)
            # Verify it's actually a fork of the target repo
            if fork.fork and fork.parent.full_name == f"{owner}/{repo_name}":
                return {
                    "success": True,
                    "message": f"Fork exists for {owner}/{repo_name}",
                    "data": {"exists": True},
                    "error": None,
                }
            return {
                "success": True,
                "message": f"No fork exists for {owner}/{repo_name}",
                "data": {"exists": False},
                "error": None,
            }
        except GithubException:
            return {
                "success": True,
                "message": f"No fork exists for {owner}/{repo_name}",
                "data": {"exists": False},
                "error": None,
            }

    except Exception as e:
        return {
            "success": False,
            "message": "Failed to check fork existence",
            "data": None,
            "error": str(e),
        }


def review_pull_request(
    repo_full_name: str,
    pr_number: int,
    title: str,
    description: str,
    requirements: Dict[str, List[str]],
    test_evaluation: Dict[str, List[str]],
    recommendation: str,
    recommendation_reason: List[str],
    action_items: List[str],
) -> ToolOutput:
    """
    Post a structured review comment on a pull request.

    Args:
        repo_full_name (str): Full name of the repository (owner/repo)
        pr_number (int): Pull request number
        title (str): Title of the PR
        description (str): Description of the changes
        requirements (Dict[str, List[str]]): Dictionary with 'met' and 'not_met' requirements
        test_evaluation (Dict[str, List[str]]): Dictionary with test evaluation details
        recommendation (str): APPROVE/REVISE/REJECT
        recommendation_reason (List[str]): List of reasons for the recommendation
        action_items (List[str]): List of required changes or improvements

    Returns:
        ToolOutput: Standardized tool output with review status and details
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

        # Format the review body using the template
        review_body = REVIEW_TEMPLATE.format(
            title=title,
            description=description,
            met_requirements=format_list(
                requirements.get("met", []), "No requirements met"
            ),
            not_met_requirements=format_list(
                requirements.get("not_met", []), "All requirements met"
            ),
            passed_tests=format_list(
                test_evaluation.get("passed", []), "No passing tests"
            ),
            failed_tests=format_list(
                test_evaluation.get("failed", []), "No failing tests"
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
        validated = recommendation.upper() == "APPROVE"
        return {
            "success": True,
            "message": f"Successfully posted review on PR #{pr_number}",
            "data": {
                "validated": validated,
                "review_body": review_body,
                "recommendation": recommendation,
            },
            "error": None,
        }
    except Exception as e:
        error_msg = f"Error posting review on PR #{pr_number}: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": "Failed to post review",
            "data": None,
            "error": error_msg,
        }


def validate_implementation(
    validated: bool,
    test_results: dict,
    criteria_status: dict,
    directory_check: dict,
    issues: list,
    required_fixes: list,
) -> ToolOutput:
    """Submit a validation result with formatted message.

    Args:
        validated: Whether the implementation passed validation
        test_results: Dict with passed and failed test lists
        criteria_status: Dict with met and not_met criteria lists
        directory_check: Dict with valid boolean and issues list
        issues: List of issues found
        required_fixes: List of fixes needed

    Returns:
        ToolOutput: Standardized tool output with validation results
    """
    try:
        # Format a detailed validation message
        message = []

        # Add test results
        if test_results and test_results.get("failed"):
            message.append("Failed Tests:")
            message.extend(f"- {test}" for test in test_results["failed"])
            message.append("")

        # Add unmet criteria
        if criteria_status and criteria_status.get("not_met"):
            message.append("Unmet Acceptance Criteria:")
            message.extend(f"- {criterion}" for criterion in criteria_status["not_met"])
            message.append("")

        # Add directory issues
        if directory_check and directory_check.get("issues"):
            message.append("Directory Structure Issues:")
            message.extend(f"- {issue}" for issue in directory_check["issues"])
            message.append("")

        # Add other issues
        if issues:
            message.append("Other Issues:")
            message.extend(f"- {issue}" for issue in issues)
            message.append("")

        # Add required fixes
        if required_fixes:
            message.append("Required Fixes:")
            message.extend(f"- {fix}" for fix in required_fixes)

        return {
            "success": True,  # Tool executed successfully
            "message": (
                "\n".join(message) if not validated else "All acceptance criteria met"
            ),
            "data": {
                "validated": validated,
                "test_results": test_results,
                "criteria_status": criteria_status,
                "directory_check": directory_check,
                "issues": issues,
                "required_fixes": required_fixes,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Validation tool failed",
            "data": None,
            "error": f"Validation tool failed: {str(e)}",
        }
