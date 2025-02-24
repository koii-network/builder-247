"""Review flow implementation."""

# Standard library imports
import os
import sys
import shutil
from git import Repo
import dotenv
from github import Github
from src.task.constants import PROMPTS
from src.utils.logging import (
    log_section,
    log_key_value,
    log_error,
    configure_logging,
)

# Conditional path adjustment before any other imports
if __name__ == "__main__":
    # Calculate path to project root
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../..")
    )
    sys.path.insert(0, project_root)

# Regular imports (PEP 8 compliant)
from src.get_file_list import get_file_list
from src.task.setup_new import setup_client
from src.utils.retry import (
    execute_tool_with_retry,
    send_message_with_retry,
)

# Ensure environment variables are loaded
dotenv.load_dotenv()


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
        raise RuntimeError(f"GitHub authentication failed: {str(e)}")


def handle_tool_response(client, response):
    """
    Handle tool responses until natural completion.
    """
    log_section("STARTING CONVERSATION")
    tool_result = None  # Track the final tool execution result
    conversation_id = response.get("conversation_id")  # Store conversation ID

    while response.get("stop_reason") == "tool_use":
        # Process all tool uses in the current response
        for tool_call in [
            block["tool_call"]
            for block in response.get("content", [])
            if block.get("type") == "tool_call"
        ]:
            try:
                # Execute the tool with retry logic
                tool_output = execute_tool_with_retry(client, tool_call)
                tool_result = tool_output  # Store the final tool result

                if tool_call["name"] == "review_pull_request":
                    return tool_output

                # Convert tool output to string if it's not already
                tool_response_str = (
                    str(tool_output) if tool_output is not None else None
                )
                if tool_response_str is None:
                    log_key_value(
                        "Warning", "Tool output is None, skipping message to Claude"
                    )
                    continue

                # Send successful tool result back to Claude with conversation state
                response = send_message_with_retry(
                    client,
                    tool_response=tool_response_str,
                    tool_use_id=tool_call["id"],
                    conversation_id=conversation_id,
                )

            except Exception as e:
                error_msg = f"Failed to execute tool {tool_call['name']}: {str(e)}"
                log_error(e, error_msg)
                # Send error back to Claude so it can try again
                try:
                    # Format error as a string for Claude
                    error_response = {
                        "success": False,
                        "error": error_msg,
                        "tool_name": tool_call["name"],
                        "input": tool_call["arguments"],
                    }
                    response = send_message_with_retry(
                        client,
                        tool_response=str(error_response),
                        tool_use_id=tool_call["id"],
                        conversation_id=conversation_id,
                    )
                except Exception as send_error:
                    log_error(send_error, "Failed to send error message to Claude")
                    raise
                continue

    log_section("CONVERSATION ENDED")
    return tool_result


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
            log_section(f"REVIEWING PR #{pr.number}: {pr.title}")
            review_pr(
                pr_url=pr.html_url,
                requirements=requirements,
                minor_issues=minor_issues,
                major_issues=major_issues,
                system_prompt=system_prompt,
            )

        except Exception as e:
            log_error(e, f"Error reviewing PR #{pr.number}")
            continue  # Continue with next PR even if one fails


def review_pr(
    pr_url: str,
    requirements,
    minor_issues,
    major_issues,
    system_prompt,
):
    """
    Review a specific pull request.
    """
    repo_path = None
    original_dir = os.getcwd()  # Store original directory
    try:
        # Parse PR URL to get components
        repo_owner, repo_name, pr_number = parse_github_pr_url(pr_url)

        # Set up repository
        repo_path, files = setup_pr_repository(repo_owner, repo_name, pr_number)

        # Change to repository directory
        os.chdir(repo_path)

        # Create new conversation
        client = setup_client()

        # Log system prompt
        log_section("SYSTEM PROMPT")
        log_key_value("System prompt", system_prompt)

        # Create conversation with system prompt
        conversation_id = client.storage.create_conversation(
            system_prompt=system_prompt
        )

        # Format requirements as bullet points
        formatted_reqs = "\n".join(f"- {req}" for req in requirements)

        # Format files list
        files_list = "\n".join(f"- {f}" for f in files)

        # Format review prompt
        review_prompt = PROMPTS["review_pr"].format(
            pr_number=pr_number,
            repo=f"{repo_owner}/{repo_name}",
            files_list=files_list,
            requirements=formatted_reqs,
            minor_issues=minor_issues,
            major_issues=major_issues,
        )

        # Send initial message
        response = send_message_with_retry(
            client, prompt=review_prompt, conversation_id=conversation_id
        )

        # Handle tool responses
        pr_review = handle_tool_response(client, response)
        if pr_review:
            return pr_review

    except Exception as e:
        log_error(e, f"Error reviewing PR {pr_url}")
        raise
    finally:
        # Clean up repository
        if repo_path and os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        # Restore original directory
        os.chdir(original_dir)


if __name__ == "__main__":
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
        "no implementation or tests, implementation is not for the correct problem",
        "Incorrect implementation, failing tests, missing critical features, "
        "no error handling, security vulnerabilities, no tests",
        "tests are poorly designed or rely too heavily on mocking",
    )
    try:
        # Set up logging with DEBUG level
        configure_logging()

        # Validate environment and authentication
        check_required_env_vars()
        validate_github_auth()

        review_all_pull_requests(
            repo_owner="koii-network",
            repo_name="builder-test",
            requirements=requirements,
            minor_issues=minor_issues,
            major_issues=major_issues,
            system_prompt=os.environ["REVIEW_SYSTEM_PROMPT"],
        )
    except Exception as e:
        log_error(e, "Script failed")
        sys.exit(1)
