"""Flow for processing todos and creating PRs."""

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
from src.utils.errors import ClientAPIError
from src.utils.logging import (
    log_section,
    log_key_value,
    log_error,
    configure_logging,
)
from src.clients.types import MessageContent, ToolCallContent
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
from src.tools.git_operations.implementations import get_current_branch
from src.workflows.setup_new import setup_client
from src.workflows.constants import PROMPTS
from src.tools.github_operations.implementations import fork_repository
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
    If a tool has return_value=True, returns immediately after executing that tool.
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
                # Check if this tool has return_value set
                tool_definition = client.tools.get(tool_call["name"])
                should_return = tool_definition and tool_definition.get(
                    "return_value", False
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

                # If this tool has return_value=True, return its result immediately
                if should_return:
                    return tool_results

            except ClientAPIError:
                # Let API errors propagate up unchanged
                raise

            except Exception as e:
                error_msg = f"Failed to execute tool {tool_call['name']}: {str(e)}"
                log_error(e, error_msg)
                # Format error as a string for Claude
                error_response = {
                    "success": False,
                    "error": error_msg,
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

    validation_results = handle_tool_response(client, response)
    if not validation_results:
        return False, "Failed to get validation result"

    # Get the last result since that's the final validation
    last_result = validation_results[-1]
    try:
        response_dict = ast.literal_eval(last_result["response"])
        if not response_dict.get("success", False):
            return False, response_dict.get("error", "Unknown validation error")
    except (ValueError, SyntaxError, AttributeError):
        return False, f"Invalid validation response: {last_result['response']}"

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
            tool_choice={"type": "required", "tool": "create_branch"},
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
            tool_choice={"type": "required", "tool": "create_pull_request"},
        )

        pr_results = handle_tool_response(client, pr_response)
        if not pr_results:
            log_error(Exception("No PR result returned"), "PR creation failed")
            return None

        # Get the last result since that's the final PR creation attempt
        pr_result = ast.literal_eval(pr_results[-1]["response"])
        if pr_result.get("success"):
            log_key_value("PR created successfully", pr_result.get("pr_url"))
            return pr_result.get("pr_url")
        else:
            log_error(Exception(pr_result.get("error")), "PR creation failed")
            return None

    except Exception as e:
        if not isinstance(e, ClientAPIError):
            log_error(e, "Error in todo_to_pr")
        raise e

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
                        log_error(e, "Script failed", False)
                        sys.exit(1)
                else:
                    log_key_value("Skipping invalid row", row)
    except Exception as e:
        log_error(e, "Script failed")
        sys.exit(1)
