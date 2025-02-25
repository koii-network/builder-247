"""Task flow implementation."""

# Standard library imports
import os
import sys
import time
from pathlib import Path
import csv
import shutil
from git import Repo
from github import Github
import dotenv
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
from anthropic.types import ToolUseBlock
from src.get_file_list import get_file_list
from agents.builder.src.tools.git_operations_old import get_current_branch
from src.workflows.setup import setup_client
from src.workflows.constants import PROMPTS
from agents.builder.src.tools.github_operations_old import fork_repository
from src.utils.retry import (
    execute_tool_with_retry,
    send_message_with_retry,
)

# Ensure environment variables are loaded
dotenv.load_dotenv()


def check_required_env_vars():
    """Check if all required environment variables are set."""
    required_vars = ["GITHUB_TOKEN", "GITHUB_USERNAME", "TASK_SYSTEM_PROMPT"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please ensure these are set in your .env file or environment."
        )


def validate_github_auth():
    """Validate GitHub authentication."""
    try:
        gh = Github(os.getenv("GITHUB_TOKEN"))
        user = gh.get_user()
        username = user.login
        if username != os.getenv("GITHUB_USERNAME"):
            raise ValueError(
                f"GitHub token belongs to {username}, but GITHUB_USERNAME is set to {os.getenv('GITHUB_USERNAME')}"
            )
        log_key_value("Successfully authenticated as", username)
    except Exception as e:
        raise RuntimeError(f"GitHub authentication failed: {str(e)}")


def handle_tool_response(client, response):
    """
    Handle tool responses until natural completion.
    """
    tool_result = None  # Track the final tool execution result
    conversation_id = response.conversation_id  # Store conversation ID

    while response.stop_reason == "tool_use":
        # Process all tool uses in the current response
        for tool_use in [b for b in response.content if isinstance(b, ToolUseBlock)]:
            try:
                # Execute the tool with retry logic
                tool_output = execute_tool_with_retry(client, tool_use)
                tool_result = tool_output  # Store the final tool result

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

                # Send successful tool result back to Claude with conversation state
                response = send_message_with_retry(
                    client,
                    tool_response=tool_response_str,
                    tool_use_id=tool_use.id,
                    conversation_id=conversation_id,
                )

            except Exception as e:
                error_msg = f"Failed to execute tool {tool_use.name}: {str(e)}"
                log_error(e, error_msg)
                # Send error back to Claude so it can try again
                try:
                    # Format error as a string for Claude
                    error_response = {
                        "success": False,
                        "error": error_msg,
                        "tool_name": tool_use.name,
                        "input": tool_use.input,
                    }
                    response = send_message_with_retry(
                        client,
                        tool_response=str(error_response),
                        tool_use_id=tool_use.id,
                        conversation_id=conversation_id,
                    )
                except Exception as send_error:
                    log_error(send_error, "Failed to send error message to Claude")
                    raise
                continue
    return tool_result


def validate_acceptance_criteria(client, conversation_id, todo, acceptance_criteria):
    """
    Validate that all acceptance criteria are met, including passing tests.
    Returns tuple of (bool, str) indicating success/failure and reason for failure.
    """
    log_section("VALIDATING ACCEPTANCE CRITERIA")

    validation_prompt = PROMPTS["validate_criteria"].format(
        todo=todo, acceptance_criteria=acceptance_criteria
    )

    response = send_message_with_retry(
        client,
        prompt=validation_prompt,
        conversation_id=conversation_id,
    )

    validation_result = handle_tool_response(client, response)
    if not validation_result:
        return False, "Failed to get validation result"

    if not validation_result.get("success", False):
        return False, validation_result.get("error", "Unknown validation error")

    return True, ""


def todo_to_pr(
    repo_owner,
    repo_name,
    todo,
    acceptance_criteria,
    system_prompt,
    repo_path=None,
):
    """
    Task flow with proper directory handling
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

    # Set up repository and working directory
    original_dir = os.getcwd()
    try:
        # Clean existing repository (in case of partial failures)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)

        # Create parent directory first
        os.makedirs(os.path.dirname(repo_path), exist_ok=True)

        # Fork and clone repository
        log_section("FORKING AND CLONING REPOSITORY")
        fork_result = fork_repository(f"{repo_owner}/{repo_name}", repo_path)
        if not fork_result["success"]:
            raise Exception(f"Fork failed: {fork_result.get('error')}")

        # Enter repo directory
        os.chdir(repo_path)

        # Create client and conversation with system prompt
        client = setup_client()
        conversation_id = client.create_conversation(system_prompt=system_prompt)

        # Configure Git user info
        repo = Repo(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", os.environ["GITHUB_USERNAME"])
            config.set_value(
                "user",
                "email",
                f"{os.environ['GITHUB_USERNAME']}@users.noreply.github.com",
            )

        # Create branch
        log_section("CREATING BRANCH")
        setup_prompt = PROMPTS["setup_repository"].format(todo=todo)
        branch_response = send_message_with_retry(
            client,
            prompt=setup_prompt,
            conversation_id=conversation_id,
            tool_choice={"type": "tool", "name": "create_branch"},
        )
        handle_tool_response(client, branch_response)
        branch_info = get_current_branch()
        branch_name = branch_info.get("output") if branch_info.get("success") else None

        # Implementation loop - try up to 3 times to meet all acceptance criteria
        max_implementation_attempts = 3
        validation_message = ""  # Initialize validation message
        for attempt in range(max_implementation_attempts):
            log_section(
                f"IMPLEMENTATION ATTEMPT {attempt + 1}/{max_implementation_attempts}"
            )

            # Get the list of files
            files = get_file_list(repo_path)
            log_key_value("Found files", len(files))
            files_directory = ", ".join(map(str, files))

            # If this is a retry, modify the prompt to focus on fixing issues
            if attempt > 0:
                execute_todo_prompt = PROMPTS["fix_implementation"].format(
                    todo=todo,
                    files_directory=files_directory,
                    previous_issues=validation_message,
                )
            else:
                execute_todo_prompt = PROMPTS["execute_todo"].format(
                    todo=todo,
                    files_directory=files_directory,
                )

            execute_todo_response = send_message_with_retry(
                client,
                prompt=execute_todo_prompt,
                conversation_id=conversation_id,
            )
            handle_tool_response(client, execute_todo_response)

            # Validate acceptance criteria
            is_valid, validation_message = validate_acceptance_criteria(
                client, conversation_id, todo, acceptance_criteria
            )

            if is_valid:
                log_key_value(
                    "Validation", "All acceptance criteria met, proceeding to create PR"
                )
                break

            if attempt == max_implementation_attempts - 1:
                log_error(
                    Exception(validation_message),
                    f"Failed to meet acceptance criteria after {max_implementation_attempts} attempts",
                )
                return None

            log_key_value(f"Validation attempt {attempt + 1}", validation_message)
            time.sleep(5)  # Brief pause before retry

        # Create PR with retries
        log_section("CREATING PULL REQUEST")
        create_pr_prompt = PROMPTS["create_pr"].format(
            repo_full_name=f"{repo_owner}/{repo_name}",
            head=branch_name,
            base="main",
            todo=todo,
            acceptance_criteria=acceptance_criteria,
        )
        pr_response = send_message_with_retry(
            client,
            prompt=create_pr_prompt,
            tool_choice={"type": "tool", "name": "create_pull_request"},
        )

        pr_result = handle_tool_response(client, pr_response)

        if pr_result.get("success"):
            log_key_value("PR created successfully", pr_result.get("pr_url"))
            return pr_result.get("pr_url")
        else:
            log_error(Exception(pr_result.get("error")), "PR creation failed")
            return None

    except Exception as e:
        log_error(e, "Error in todo_to_pr")
        raise

    finally:
        os.chdir(original_dir)  # Restore original directory


if __name__ == "__main__":
    try:
        # Set up logging with DEBUG level
        configure_logging()

        # Validate environment and authentication
        check_required_env_vars()
        validate_github_auth()

        todos_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "data"
            / "test_todos.csv"
        )

        if not todos_path.exists():
            log_error(
                Exception(f"Todos file not found at {todos_path}"), "File not found"
            )
            sys.exit(1)

        with open(todos_path, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for i, row in enumerate(reader):
                if len(row) >= 2:
                    todo, acceptance_criteria = row[0], row[1]
                    try:
                        log_section(f"PROCESSING TODO {i}")
                        todo_to_pr(
                            todo=todo.strip(),
                            repo_owner="koii-network",
                            repo_name="builder-test",
                            acceptance_criteria=acceptance_criteria.strip(),
                            repo_path=f"./repo_{i}",  # Unique path per task
                            system_prompt=os.environ["TASK_SYSTEM_PROMPT"],
                        )
                    except Exception as e:
                        log_error(e, f"Failed to process todo {i}")
                        continue
                else:
                    log_key_value("Skipping invalid row", row)
    except Exception as e:
        log_error(e, "Script failed")
        sys.exit(1)
