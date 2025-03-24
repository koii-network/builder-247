"""Module for GitHub operations."""

import os
from typing import Dict, List, Any
from github import Github, Auth, GithubException
from dotenv import load_dotenv
from src.tools.git_operations.implementations import (
    fetch_remote,
    pull_remote,
)
from src.utils.logging import log_key_value, log_error
from src.types import ToolOutput
from src.workflows.utils import get_fork_name

from git import Repo, GitCommandError
from src.tools.github_operations.templates import TEMPLATES
from github.PullRequest import PullRequest

import csv
import uuid
import json

# Load environment variables from .env file
load_dotenv()


def _get_github_client(github_token: str) -> Github:
    """
    Get an authenticated GitHub client.

    Args:
        github_token: GitHub token for authentication

    Returns:
        Github: Authenticated GitHub client

    Raises:
        ValueError: If github_token is not provided
    """
    if not github_token:
        raise ValueError("GitHub token is required")
    return Github(auth=Auth.Token(github_token))


def create_pull_request(
    repo_owner: str,
    repo_name: str,
    head_branch: str,
    pr_template: str,
    github_token: str,
    github_username: str,
    data: Dict[str, Any],
    base_branch: str = "main",
    **kwargs,
) -> ToolOutput:
    """Create PR with formatted description.

    Args:
        repo_owner: Owner of the source repository
        repo_name: Name of the source repository
        title: PR title
        head_branch: Head branch name (branch the PR is coming from)
        description: PR description
        tests: List of test descriptions
        todo: Original todo task
        acceptance_criteria: Task acceptance criteria
        base_branch: Base branch name (default: main)
        github_token: Optional GitHub token for authentication

    Returns:
        ToolOutput: Standardized tool output with PR URL on success
    """
    try:
        gh = _get_github_client(github_token)
        repo_full_name = f"{repo_owner}/{repo_name}"

        head = f"{github_username}:{head_branch}"
        log_key_value("Creating PR with head", head)

        title = data["title"]
        if not title:
            raise ValueError("Title is required")

        body = pr_template.format(**data)

        repo = gh.get_repo(repo_full_name)
        pr = repo.create_pull(title=title, body=body, head=head, base=base_branch)
        return {
            "success": True,
            "message": f"Successfully created PR: {title}",
            "data": {"pr_url": pr.html_url},
        }
    except GithubException as e:
        log_error(e, f"GitHub API error: {str(e.data)}")
        return {
            "success": False,
            "message": f"Failed to create pull request: {str(e)}",
            "data": {"errors": e.data.get("errors", [])},
        }
    except Exception as e:
        log_error(e, f"Error creating PR: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to create pull request: {str(e)}",
            "data": None,
        }


def create_worker_pull_request(
    title: str,
    description: str,
    changes: List[str],
    tests: List[str],
    todo: str,
    repo_owner: str,
    repo_name: str,
    acceptance_criteria: List[str],
    staking_key: str,
    pub_key: str,
    staking_signature: str,
    public_signature: str,
    base_branch: str,
    github_token: str,
    github_username: str,
    head_branch: str,
    **kwargs,
) -> ToolOutput:
    """Create a pull request with worker information."""
    try:
        # Get GitHub client
        gh = _get_github_client(github_token)

        # Format lists into markdown bullets
        tests_bullets = " - " + "\n - ".join(tests)
        changes_bullets = " - " + "\n - ".join(changes)
        acceptance_criteria_bullets = " - " + "\n - ".join(acceptance_criteria)

        # Format the pull request data
        data = {
            "title": title,
            "description": description,
            "changes": changes_bullets,
            "todo": todo,
            "acceptance_criteria": acceptance_criteria_bullets,
            "tests": tests_bullets,
            "staking_key": staking_key,
            "pub_key": pub_key,
            "staking_signature": staking_signature,
            "public_signature": public_signature,
        }

        # Create the pull request
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")
        head = f"{github_username}:{head_branch}"  # Format head with username prefix
        pr = repo.create_pull(
            title=title,
            body=TEMPLATES["worker_pr_template"].format(**data),
            head=head,
            base=base_branch,
        )

        return {
            "success": True,
            "message": f"Successfully created PR: {title}",
            "data": {"pr_url": pr.html_url},
        }
    except Exception as e:
        print(f"Failed to create worker pull request: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to create worker pull request: {str(e)}",
            "data": None,
        }


def create_leader_pull_request(
    repo_owner: str,
    repo_name: str,
    title: str,
    head_branch: str,
    description: str,
    changes: str,
    tests: str,
    pr_details: List[Dict[str, str]],
    base_branch: str = "main",
    staking_key: str = None,
    pub_key: str = None,
    staking_signature: str = None,
    public_signature: str = None,
    **kwargs,
) -> ToolOutput:
    """Create a pull request for a leader node.

    Args:
        repo_owner: Owner of the source repository
        repo_name: Name of the source repository
        title: PR title
        head_branch: Head branch name (branch the PR is coming from)
        description: High-level description of the changes
        changes: Description of major changes made
        tests: Description of testing and verification performed
        pr_details: List of consolidated PRs, each containing:
            - number: PR number
            - title: PR title
            - url: Original PR URL
            - source_owner: Original PR repository owner
            - source_repo: Original PR repository name
            - description: Original PR description
            - files_changed: List of files changed in the PR
        base_branch: Base branch name (default: main)
        staking_key: Leader's staking key
        pub_key: Leader's public key
        staking_signature: Leader's staking signature
        public_signature: Leader's public signature

    Returns:
        ToolOutput: Standardized tool output with PR URL on success
    """
    log_key_value("create_leader_pull_request kwargs", str(kwargs))

    # Format the consolidated PRs into a markdown list with proper links
    consolidated_prs = "The following pull requests have been merged:\n\n"

    for pr in pr_details:
        # Add PR to the list with original URL and attribution
        consolidated_prs += f"- [#{pr['number']}: {pr['title']}]({pr['url']}) from @{pr['source_owner']}\n"

    return create_pull_request(
        repo_owner=repo_owner,
        repo_name=repo_name,
        head_branch=head_branch,
        base_branch=base_branch,
        pr_template=TEMPLATES["leader_pr_template"],
        data={
            "title": title,
            "description": description,
            "changes": changes,
            "tests": tests,
            "consolidated_prs": consolidated_prs,
            "staking_key": staking_key,
            "pub_key": pub_key,
            "staking_signature": staking_signature,
            "public_signature": public_signature,
        },
        **kwargs,
    )


def sync_fork(repo_path: str, branch: str = "main", **kwargs) -> ToolOutput:
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
                "message": f"Failed to fetch from upstream: {fetch_result.get('error')}",
                "data": None,
            }

        # Pull from upstream
        pull_result = pull_remote(repo_path, "upstream", branch)
        if not pull_result["success"]:
            return {
                "success": False,
                "message": f"Failed to pull from upstream: {pull_result.get('error')}",
                "data": None,
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
                "message": f"Failed to push to origin: {error_msg}",
                "data": None,
            }

        print("Successfully synced fork with upstream")
        return {
            "success": True,
            "message": f"Successfully synced branch {branch} with upstream",
            "data": {"branch": branch},
        }

    except Exception as e:
        error_msg = f"Unexpected error while syncing fork: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": f"Failed to sync fork: {error_msg}",
            "data": None,
        }


def check_fork_exists(owner: str, repo_name: str, **kwargs) -> ToolOutput:
    """
    Check if fork exists using GitHub API.

    Args:
        owner: Owner of the repository
        repo_name: Name of the repository

    Returns:
        ToolOutput: Standardized tool output with fork existence status
    """
    try:
        gh = _get_github_client(os.environ.get("GITHUB_TOKEN"))

        # First check if the source repo exists
        try:
            gh.get_repo(f"{owner}/{repo_name}")
        except GithubException:
            return {
                "success": False,
                "message": "Source repository not found",
                "data": None,
            }

        # Get our expected fork name
        source_repo_url = f"https://github.com/{owner}/{repo_name}"
        fork_name = get_fork_name(owner, source_repo_url, github=gh)

        # Then check if we have a fork with that name
        user = gh.get_user()
        try:
            fork = user.get_repo(fork_name)
            # Verify it's actually a fork of the target repo
            if fork.fork and fork.parent.full_name == f"{owner}/{repo_name}":
                return {
                    "success": True,
                    "message": f"Fork exists for {owner}/{repo_name}",
                    "data": {"exists": True},
                }
            return {
                "success": True,
                "message": f"No fork exists for {owner}/{repo_name}",
                "data": {"exists": False},
            }
        except GithubException:
            return {
                "success": True,
                "message": f"No fork exists for {owner}/{repo_name}",
                "data": {"exists": False},
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to check fork existence: {str(e)}",
            "data": None,
        }


def review_pull_request(
    repo_owner: str,
    repo_name: str,
    pr_number: int,
    title: str,
    description: str,
    unmet_requirements: List[str],
    test_evaluation: Dict[str, List[str]],
    recommendation: str,
    recommendation_reason: List[str],
    action_items: List[str],
    staking_key: str,
    pub_key: str,
    staking_signature: str,
    public_signature: str,
    **kwargs,
) -> ToolOutput:
    """
    Post a structured review comment on a pull request.

    Args:
        repo_owner (str): Owner of the repository
        repo_name (str): Name of the repository
        pr_number (int): Pull request number
        title (str): Title of the PR
        description (str): Description of the changes
        unmet_requirements (List[str]): List of unmet requirements
        test_evaluation (Dict[str, List[str]]): Dictionary with test evaluation details
        recommendation (str): APPROVE/REVISE/REJECT
        recommendation_reason (List[str]): List of reasons for the recommendation
        action_items (List[str]): List of required changes or improvements
        staking_key (str): Reviewer's staking key
        pub_key (str): Reviewer's public key
        staking_signature (str): Reviewer's staking signature
        public_signature (str): Reviewer's public signature

    Returns:
        ToolOutput: Standardized tool output with review status and details
    """
    try:
        gh = _get_github_client(os.environ.get("GITHUB_TOKEN"))
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")
        pr = repo.get_pull(pr_number)

        # Format lists into markdown bullet points
        def format_list(items: List[str], empty_message: str = "None") -> str:
            if not items:
                return f"*{empty_message}*"
            return "- " + "\n- ".join(items)

        # Format the review body using the template
        review_body = TEMPLATES["review_template"].format(
            title=title,
            description=description,
            unmet_requirements=format_list(unmet_requirements, "All requirements met"),
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
            staking_key=staking_key,
            pub_key=pub_key,
            staking_signature=staking_signature,
            public_signature=public_signature,
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
        }
    except Exception as e:
        error_msg = f"Error posting review on PR #{pr_number}: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "message": f"Failed to post review: {error_msg}",
            "data": None,
        }


def validate_implementation(
    validated: bool,
    test_results: dict,
    criteria_status: dict,
    directory_check: dict,
    issues: list,
    required_fixes: list,
    **kwargs,
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
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Validation tool failed: {str(e)}",
            "data": None,
        }


def generate_analysis(
    bugs=None,
    vulnerabilities=None,
    code_quality_issues=None,
    file_name="bugs.csv",
    repo_url=None,
    **kwargs,
) -> ToolOutput:
    """
    Generate analysis of bugs, security vulnerabilities, and code quality issues.
    Creates a CSV file with the issues and acceptance criteria.

    Args:
        bugs: List of bugs found in the repository
        vulnerabilities: List of security vulnerabilities found
        code_quality_issues: List of code quality issues found
        file_name: Name of the output file
        repo_url: URL of the repository that was analyzed

    Returns:
        ToolOutput: Standardized tool output with success status and file path
    """
    try:
        data_dir = os.environ.get("DATA_DIR")
        if not data_dir:
            raise ValueError("DATA_DIR environment variable must be set")

        # Ensure the file has a .csv extension
        if not file_name.endswith(".csv"):
            file_name = f"{os.path.splitext(file_name)[0]}.csv"
            print(f"Changed file extension to .csv: {file_name}")

        print(f"Using file name: {file_name}")

        # Combine all issues into a single list
        all_issues = []

        # Add bugs
        if bugs and isinstance(bugs, list):
            all_issues.extend(bugs)

        # Add vulnerabilities
        if vulnerabilities and isinstance(vulnerabilities, list):
            all_issues.extend(vulnerabilities)

        # Add code quality issues
        if code_quality_issues and isinstance(code_quality_issues, list):
            all_issues.extend(code_quality_issues)

        # Create the full file path
        file_path = os.path.join(data_dir, file_name)

        # Write the issues to a CSV file
        with open(file_path, "w", newline="") as csvfile:
            fieldnames = ["bug", "acceptance_criteria"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for issue in all_issues:
                try:
                    # Get the description
                    description = issue.get("description", "")

                    # Handle acceptance_criteria as either a string or a list
                    acceptance_criteria = issue.get("acceptance_criteria", "")

                    # If acceptance_criteria is a list, join it into a string
                    if isinstance(acceptance_criteria, list):
                        acceptance_criteria = "\n".join(
                            [f"- {criterion}" for criterion in acceptance_criteria]
                        )

                    writer.writerow(
                        {
                            "bug": description,
                            "acceptance_criteria": acceptance_criteria,
                        }
                    )
                except Exception as e:
                    print(f"Error processing issue: {str(e)}")
                    print(f"Issue data: {issue}")

        # Get the absolute path to the file
        abs_file_path = os.path.abspath(file_path)

        # Log the file creation
        print(f"Created CSV file with {len(all_issues)} issues at {abs_file_path}")

        return {
            "success": True,
            "message": f"Successfully created CSV file with {len(all_issues)} issues",
            "data": {
                "file_path": abs_file_path,
                "issue_count": len(all_issues),
                "repo_url": repo_url,
                "bugs": bugs,
            },
        }
    except Exception as e:
        error_msg = f"Error generating analysis: {str(e)}"
        print(error_msg)
        import traceback

        traceback.print_exc()
        return {"success": False, "message": error_msg, "data": None}


def merge_pull_request(
    repo_full_name: str, pr_number: int, merge_method: str = "merge", **kwargs
) -> ToolOutput:
    """
    Merge a pull request using the GitHub API.

    Args:
        repo_full_name: Full name of repository (owner/repo)
        pr_number: Pull request number to merge
        merge_method: Merge method to use (merge, squash, rebase)

    Returns:
        ToolOutput: Standardized tool output with success status and error message if any
    """
    try:
        log_key_value("Merging PR", f"{repo_full_name}#{pr_number}")

        # Get GitHub client
        gh = _get_github_client(os.environ.get("GITHUB_TOKEN"))

        # Get repository
        repo = gh.get_repo(repo_full_name)

        # Get pull request
        pr = repo.get_pull(pr_number)

        # Check if PR is mergeable
        if not pr.mergeable:
            return {
                "success": False,
                "message": f"PR #{pr_number} is not mergeable",
                "data": {
                    "pr_number": pr_number,
                    "mergeable": False,
                    "state": pr.state,
                },
            }

        # Merge the PR
        merge_result = pr.merge(merge_method=merge_method)

        return {
            "success": True,
            "message": f"Successfully merged PR #{pr_number}",
            "data": {
                "pr_number": pr_number,
                "merged": True,
                "sha": merge_result.sha,
            },
        }
    except GithubException as e:
        log_error(e, f"Failed to merge PR #{pr_number}")
        return {
            "success": False,
            "message": f"GitHub API error: {str(e)}",
            "data": {
                "pr_number": pr_number,
                "error_code": e.status,
                "error_message": e.data.get("message", "Unknown error"),
            },
        }
    except Exception as e:
        log_error(e, f"Failed to merge PR #{pr_number}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "data": {
                "pr_number": pr_number,
            },
        }


def generate_tasks(
    tasks: List[Dict[str, Any]] = None,
    file_name: str = "tasks.csv",
    repo_url: str = None,
    **kwargs,
) -> dict:
    """Generate a Task List for the repository.

    Args:
        tasks: List of task dictionaries, each containing:
            - title: Task title
            - description: Task description
            - acceptance_criteria: List of acceptance criteria

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - task_count: Number of tasks written
                - tasks: List of task dictionaries
            - error: Error message if any
    """
    try:
        data_dir = os.environ.get("DATA_DIR")
        if not data_dir:
            raise ValueError("DATA_DIR environment variable must be set")

        # Full path for the CSV file
        file_path = os.path.join(data_dir, file_name)

        # Write tasks to CSV
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            # Write headers
            writer.writerow(["Title", "Description", "Acceptance Criteria"])
            # Write tasks
            for task in tasks:
                writer.writerow(
                    [
                        task["title"],
                        task["description"],
                        "\n".join(task["acceptance_criteria"]),
                    ]
                )

        return {
            "success": True,
            "message": f"Successfully generated {len(tasks)} tasks",
            "data": {
                "task_count": len(tasks),
                "tasks": tasks,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to generate tasks: {str(e)}",
            "data": None,
            "error": str(e),
        }


def regenerate_tasks(
    tasks: List[Dict[str, Any]] = None,
) -> dict:
    """Regenerate the tasks.

    Args:
        tasks: List of task dictionaries, each containing:
            - title: Task title
            - description: Task description
            - acceptance_criteria: List of acceptance criteria
            - uuid: UUID of the task

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - task_count: Number of tasks written
                - tasks: List of task dictionaries
            - error: Error message if any
    """
    try:
        return {
            "success": True,
            "message": f"Successfully regenerated {len(tasks)} tasks",
            "data": {
                "task_count": len(tasks),
                "tasks": tasks,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to regenerate tasks: {str(e)}",
            "data": None,
            "error": str(e),
        }


def validate_tasks(decisions: List[Dict[str, Any]]) -> dict:
    """Validate the tasks.

    Args:
        decisions: List of decisions, each containing:
            - uuid: UUID of the task
            - comment: Comment on the task
            - decision: Decision on the task, True or False

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - decision_count: Number of decisions
                - decisions: Dictionary of decision dictionaries
            - error: Error message if any
    """
    try:
        decisions_dict = {}
        for decision in decisions:
            if decision["decision"] == True:
                decisions_dict[decision["uuid"]] = decision
        return {
            "success": True,
            "message": f"Successfully validated {len(decisions)} tasks",
            "data": {
                "decision_count": len(decisions_dict),
                "decisions": decisions_dict,
            },
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to validate tasks: {str(e)}",
            "data": None,
            "error": str(e),
        }


def create_task_dependency(task_uuid: str, dependency_tasks: List[str]) -> dict:
    """Create the task dependency for a task.

    Args:
        task_uuid: UUID of the task
        dependency_tasks: List of UUIDs of dependency tasks

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - task_uuid: UUID of the task
                - dependency_tasks: List of UUIDs of dependency tasks
    """
    try:
        # Create a new dict one is task_uuid and value is dependency_tasks
        dependency_tasks_dict = {task_uuid: dependency_tasks}
        return {
            "success": True,
            "message": f"Successfully updated dependency tasks for {task_uuid}",
            "data": dependency_tasks_dict,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to update dependency tasks: {str(e)}",
            "data": None,
            "error": str(e),
        }


def generate_issues(
    issues: List[Dict[str, Any]] = None,
) -> dict:
    """Generate issues for the repository.

    Args:
        issues: List of issue dictionaries, each containing:
            - title: Issue title
            - description: Issue description
            - acceptance_criteria: List of acceptance criteria

    Returns:
        dict: Result of the operation containing:
            - success: Whether the operation succeeded
            - message: Success/error message
            - data: Dictionary containing:
                - issue_count: Number of issues generated
                - issues: List of issue dictionaries with UUIDs
            - error: Error message if any
    """
    try:
        for issue in issues:
            issue_uuid = str(uuid.uuid4())
            issue["uuid"] = issue_uuid
        return {
            "success": True,
            "message": f"Successfully generated {len(issues)} issues",
            "data": {
                "issue_count": len(issues),
                "issues": issues,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to generate issues: {str(e)}",
            "data": None,
            "error": str(e),
        }


def create_github_issue(
    repo_full_name: str,
    title: str,
    description: str,
) -> ToolOutput:
    """Create a GitHub issue.

    Args:
        repo_full_name: Full name of repository (owner/repo)
        title: Issue title
        description: Issue description

    Returns:
        ToolOutput: Standardized tool output with success status and error message if any
    """
    try:
        gh = _get_github_client()
        repo = gh.get_repo(repo_full_name)
        issue = repo.create_issue(title=title, body=description)
        return {
            "success": True,
            "message": f"Successfully created issue: {title}",
            "data": {"issue_url": issue.html_url, "issue_number": issue.number},
        }
    except GithubException as e:
        return {
            "success": False,
            "message": f"Failed to create issue: {str(e)}",
            "data": {"errors": e.data.get("errors", [])},
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create issue: {str(e)}",
            "data": None,
        }


def check_repository_exists(repo_owner: str, repo_name: str, github_token: str) -> bool:
    """Check if a repository exists."""
    try:
        gh = _get_github_client(github_token)

        # First check if the source repo exists
        try:
            gh.get_repo(f"{repo_owner}/{repo_name}")
        except GithubException:
            return False

        return True
    except Exception as e:
        print(f"Failed to check repository existence: {str(e)}")
        return False


def get_pull_request(
    repo_owner: str, repo_name: str, pr_number: int, github_token: str
) -> PullRequest:
    """Get a pull request by number."""
    try:
        gh = _get_github_client(github_token)
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")
        pr = repo.get_pull(pr_number)
        return pr
    except Exception as e:
        print(f"Failed to get pull request: {str(e)}")
        return None
