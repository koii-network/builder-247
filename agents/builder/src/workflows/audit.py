"""Review flow implementation."""

# Standard library imports
import os
import sys
import shutil
from git import Repo
import dotenv
from github import Github
from src.workflows.prompts import PROMPTS, REVIEW_SYSTEM_PROMPT
from src.utils.errors import ClientAPIError
from src.utils.logging import (
    log_section,
    log_key_value,
    log_error,
    configure_logging,
)
from agents.builder.src.types import MessageContent, ToolCallContent
from src.database import get_db
from typing import List
import json
import ast

# Conditional path adjustment before any other imports
if __name__ == "__main__":
    # Calculate path to project root
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../..")
    )
    sys.path.insert(0, project_root)

# Regular imports (PEP 8 compliant)
from src.get_file_list import get_file_list
from agents.builder.src.workflows.setup_repo import setup_client
from src.utils.retry import (
    execute_tool_with_retry,
    send_message_with_retry,
)

# Ensure environment variables are loaded
dotenv.load_dotenv()

# Get database instance
db = get_db()


def check_required_env_vars():
    """Check if all required environment variables are set."""
    required_vars = ["GITHUB_TOKEN", "GITHUB_USERNAME"]
    missing_vars = [var for var in required_vars if var not in os.environ]

    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please ensure these are set in your .env file or environment."
        )


def validate_github_auth():
    """Validate GitHub authentication."""
    try:
        gh = Github(os.environ["GITHUB_TOKEN"])
        user = gh.get_user()
        username = user.login
        if username != os.environ["GITHUB_USERNAME"]:
            raise ValueError(
                f"GitHub token belongs to {username}, but GITHUB_USERNAME is set to {os.environ['GITHUB_USERNAME']}"
            )
        log_key_value("Successfully authenticated as", username)
    except Exception as e:
        log_error(e, "GitHub authentication failed")
        raise RuntimeError(str(e))


def get_tool_calls(msg: MessageContent) -> List[ToolCallContent]:
    """Return all tool call blocks from the message."""
    tool_calls = []
    for block in msg["content"]:
        if block["type"] == "tool_call":
            tool_calls.append(block["tool_call"])
    return tool_calls


def handle_tool_response(client, response):
    """
    Handle tool responses until natural completion.
    If a tool has final_tool=True, returns immediately after executing that tool.
    """
    conversation_id = response["conversation_id"]  # Store conversation ID

    while True:
        tool_calls = get_tool_calls(response)
        if not tool_calls:
            break

        # Process all tool calls in the current response
        tool_results = []
        for tool_call in tool_calls:
            try:
                # Check if this tool has final_tool set
                tool_definition = client.tools.get(tool_call["name"])
                should_return = tool_definition and tool_definition.get(
                    "final_tool", False
                )

                # Execute the tool with retry logic
                tool_output = execute_tool_with_retry(client, tool_call)

                # Convert tool output to string if it's not already
                tool_response_str = (
                    str(tool_output) if tool_output is not None else None
                )
                if tool_response_str is None:
                    log_error(
                        Exception("Tool output is None, skipping message to Claude"),
                        "Warning",
                    )
                    continue

                # Add to results list
                tool_results.append(
                    {"tool_call_id": tool_call["id"], "response": tool_response_str}
                )

                # If this tool has final_tool=True, return its result immediately
                if should_return:
                    return tool_results

            except ClientAPIError:
                # API errors are from our code, so we log them
                raise

            except Exception as e:
                # Format error as a string for Claude but don't log it
                error_response = {
                    "success": False,
                    "error": str(e),
                    "tool_name": tool_call["name"],
                    "input": tool_call["arguments"],
                }
                tool_results.append(
                    {"tool_call_id": tool_call["id"], "response": str(error_response)}
                )

        # Send all tool results back to Claude in a single message
        try:
            response = send_message_with_retry(
                client,
                tool_response=json.dumps(tool_results),
                conversation_id=conversation_id,
            )
        except Exception as send_error:
            log_error(send_error, "Failed to send tool results to Claude")
            raise

    return tool_results


def setup_pr_repository(
    repo_owner: str, repo_name: str, pr_number: int
) -> tuple[str, list[str]]:
    """
    Set up a local repository with the PR code checked out.

    Args:
        repo_owner: Owner of the repository
        repo_name: Name of the repository
        pr_number: Pull request number to check out

    Returns:
        tuple[str, list[str]]: Tuple containing:
            - Path to the repository
            - List of files in the repository
    """
    # Generate sequential repo path
    base_dir = os.path.abspath("./repos")
    os.makedirs(base_dir, exist_ok=True)

    # Find first available number
    counter = 0
    while True:
        candidate_path = os.path.join(base_dir, f"repo_{counter}")
        if not os.path.exists(candidate_path):
            repo_path = candidate_path
            break
        counter += 1

    try:
        # Clean existing repository (in case of partial failures)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)

        # Create parent directory
        os.makedirs(os.path.dirname(repo_path), exist_ok=True)

        # Clone repository
        gh = Github(os.environ["GITHUB_TOKEN"])
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")

        log_key_value("Cloning repository to", repo_path)
        git_repo = Repo.clone_from(repo.clone_url, repo_path)

        # Fetch PR
        log_key_value("Fetching PR", f"#{pr_number}")
        git_repo.remote().fetch(f"pull/{pr_number}/head:pr_{pr_number}")

        # Checkout PR branch
        log_key_value("Checking out PR branch", f"pr_{pr_number}")
        git_repo.git.checkout(f"pr_{pr_number}")

        # Get list of files
        files = get_file_list(repo_path)
        log_key_value("Found files", len(files))

        return repo_path, files

    except Exception as e:
        log_error(e, "Error setting up PR repository")
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        raise


def parse_github_pr_url(pr_url: str) -> tuple[str, str, int]:
    """
    Parse a GitHub pull request URL to extract owner, repo name, and PR number.

    Args:
        pr_url: GitHub pull request URL (e.g., 'https://github.com/owner/repo/pull/123')

    Returns:
        Tuple of (owner, repo_name, pr_number)

    Raises:
        ValueError: If the URL format is invalid
    """
    try:
        # Remove trailing slash if present
        pr_url = pr_url.rstrip("/")

        # Handle both HTTPS and SSH formats
        if pr_url.startswith("https://github.com/"):
            path = pr_url.replace("https://github.com/", "")
        elif pr_url.startswith("git@github.com:"):
            path = pr_url.replace("git@github.com:", "")
        else:
            raise ValueError(
                "URL must start with 'https://github.com/' or 'git@github.com:'"
            )

        # Split path into components
        parts = path.split("/")
        if len(parts) != 4 or parts[2] != "pull" or not parts[3].isdigit():
            raise ValueError(
                "Invalid PR URL format. Expected format: owner/repo/pull/number"
            )

        return parts[0], parts[1], int(parts[3])
    except Exception as e:
        raise ValueError(f"Failed to parse GitHub PR URL: {str(e)}")


def review_all_pull_requests(
    repo_owner, repo_name, requirements, minor_issues, major_issues, system_prompt
):
    """
    Review all open pull requests in the specified repository.
    """
    # Set up clients
    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(f"{repo_owner}/{repo_name}")

    # Get all open PRs
    open_prs = repo.get_pulls(state="open")
    log_key_value("Found open pull requests", open_prs.totalCount)

    # Review each PR
    for pr in open_prs:
        try:
            log_section(f"REVIEWING PR #{pr.number}")
            review_pr(
                pr.html_url,
                requirements,
                minor_issues,
                major_issues,
                system_prompt,
            )
        except Exception as e:
            log_error(e, f"Error reviewing PR #{pr.number}")


def review_pr(
    pr_url: str,
    requirements,
    minor_issues,
    major_issues,
    system_prompt,
):
    """
    Review a pull request and return the validation result.

    Args:
        pr_url: URL of the pull request to review
        requirements: List of requirements to check
        minor_issues: List of minor issues to check for
        major_issues: List of major issues to check for
        system_prompt: System prompt for Claude

    Returns:
        bool: True if PR is approved, False otherwise
    """
    try:
        # Parse PR URL
        repo_owner, repo_name, pr_number = parse_github_pr_url(pr_url)

        # Set up repository
        repo_path, files = setup_pr_repository(repo_owner, repo_name, pr_number)

        try:
            # Create client and conversation
            client = setup_client()
            log_section("SYSTEM PROMPT")
            log_key_value("System prompt", system_prompt)
            conversation_id = client.create_conversation(system_prompt=system_prompt)

            # Change to repository directory
            os.chdir(repo_path)

            # Send review prompt
            review_prompt = PROMPTS["review_pr"].format(
                pr_number=pr_number,
                repo=f"{repo_owner}/{repo_name}",
                files_list=", ".join(files),
                requirements=requirements,
                minor_issues=minor_issues,
                major_issues=major_issues,
            )

            # Let the agent analyze code and run tests first
            response = send_message_with_retry(
                client,
                prompt=review_prompt,
                conversation_id=conversation_id,
            )

            # Handle tool responses until we get a review result
            review_results = handle_tool_response(client, response)
            if not review_results:
                log_error(Exception("No review result returned"), "Review failed")
                return False

            # Get the last result since that's the final review
            last_result = review_results[-1]
            review_result = ast.literal_eval(last_result["response"])
            if review_result.get("success"):
                log_key_value("Review completed", "PR reviewed successfully")
                return review_result.get("validated", False)
            else:
                log_error(Exception(review_result.get("error")), "Review failed")
                return False

        finally:
            # Clean up repository
            os.chdir("..")
            shutil.rmtree(repo_path)

    except Exception as e:
        if not isinstance(e, ClientAPIError):
            log_error(e, "Error reviewing PR")
        raise e


if __name__ == "__main__":
    try:
        # Set up logging
        configure_logging()

        # Validate environment and authentication
        check_required_env_vars()
        validate_github_auth()

        # Get command line arguments
        if len(sys.argv) < 2:
            print("Usage: python review_flow_new.py <pr_url>")
            sys.exit(1)

        pr_url = sys.argv[1]
        requirements = [
            "Implementation matches problem description",
            "All tests pass",
            "Implementation is in a single file in the /src directory",
            "tests are in a single file in the /tests directory",
            "No other files are modified",
        ]

        minor_issues = (
            "test coverage could be improved but core functionality is tested",
            "implementation and tests exist but are not in the /src and /tests directories",
            "other files are modified",
        )

        major_issues = (
            "Incorrect implementation, failing tests, missing critical features, "
            "no error handling, security vulnerabilities, no tests",
            "tests are poorly designed or rely too heavily on mocking",
        )

        # Review PR
        review_pr(
            pr_url=pr_url,
            requirements=requirements,
            minor_issues=minor_issues,
            major_issues=major_issues,
            system_prompt=REVIEW_SYSTEM_PROMPT,
        )

    except Exception as e:
        log_error(e, "Script failed")
        sys.exit(1)
