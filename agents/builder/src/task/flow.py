# Standard library imports
import os
import sys
from datetime import datetime
import time
from pathlib import Path
import csv
import shutil
from git import Repo
import dotenv
import logging

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
from src.tools.git_operations import get_current_branch
from src.task.setup import setup_client
from src.task.constants import PROMPTS
from src.tools.github_operations import fork_repository
from src.task.retry_utils import (
    execute_tool_with_retry,
    send_message_with_retry,
    is_retryable_error,
)

logger = logging.getLogger(__name__)

dotenv.load_dotenv()


def handle_tool_response(client, response, tool_choice={"type": "any"}):
    """
    Handle tool responses recursively until natural completion.
    """
    logger.info("Starting conversation")
    tool_result = None  # Track the final tool execution result

    while response.stop_reason == "tool_use":
        # Process all tool uses in the current response
        for tool_use in [b for b in response.content if isinstance(b, ToolUseBlock)]:
            logger.info(f"Processing tool: {tool_use.name}")
            logger.debug(f"Tool input: {tool_use.input}")
            logger.debug(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            try:
                # Execute the tool with retry logic
                tool_output = execute_tool_with_retry(client, tool_use)
                tool_result = tool_output  # Store the final tool result
                logger.debug(f"Tool output: {tool_output}")
            except Exception as e:
                error_msg = f"Failed to execute tool {tool_use.name}: {str(e)}"
                logger.error(error_msg)
                # Send error back to Claude so it can try again
                try:
                    # Format error as a string for Claude
                    error_response = str(
                        {
                            "success": False,
                            "error": error_msg,
                            "tool_name": tool_use.name,
                            "input": tool_use.input,
                        }
                    )
                    response = send_message_with_retry(
                        client,
                        tool_response=error_response,
                        tool_use_id=tool_use.id,
                        conversation_id=response.conversation_id,
                        tool_choice=tool_choice,
                    )
                except Exception as send_error:
                    logger.error(
                        f"Failed to send error message to Claude: {str(send_error)}"
                    )
                    raise
                logger.debug(f"Response: {response}")
                continue

            # Send successful tool result back to AI with retry logic for server errors
            max_retries = 5
            retry_count = 0
            last_error = None
            while retry_count < max_retries:
                try:
                    response = send_message_with_retry(
                        client,
                        tool_response=str(tool_output),
                        tool_use_id=tool_use.id,
                        conversation_id=response.conversation_id,
                        tool_choice=tool_choice,
                    )
                    logger.debug(f"Response: {response}")
                    break
                except Exception as e:
                    if not is_retryable_error(e):
                        raise  # Don't retry client errors
                    last_error = e
                    retry_count += 1
                    if retry_count < max_retries:
                        sleep_time = min(4 * (2 ** (retry_count - 1)), 60)
                        logger.info(
                            f"Attempt {retry_count} failed, retrying in {sleep_time} seconds..."
                        )
                        time.sleep(sleep_time)
                    else:
                        logger.error(
                            f"Failed to send message after {max_retries} attempts"
                        )
                        raise last_error

    logger.info("Conversation ended")
    return tool_result  # Return the final tool execution result


def validate_acceptance_criteria(
    client, conversation_id, repo_path, todo, acceptance_criteria
):
    """
    Validate that all acceptance criteria are met, including passing tests.
    Returns tuple of (bool, str) indicating success/failure and reason for failure.
    """
    logger.info("Validating acceptance criteria...")

    # Format validation prompt
    validation_prompt = (
        "Please validate that the implementation meets all acceptance criteria:\n"
        f"Acceptance Criteria:\n{acceptance_criteria}\n\n"
        "Follow these steps:\n"
        "1. Run the tests and verify they all pass\n"
        "2. Check each acceptance criterion\n"
        "3. If any criteria are not met, explain what needs to be fixed\n"
        "4. If all criteria are met, confirm success\n"
    )

    response = client.send_message(
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
        fork_result = fork_repository(f"{repo_owner}/{repo_name}", repo_path)
        if not fork_result["success"]:
            raise Exception(f"Fork failed: {fork_result.get('error')}")

        # Enter repo directory
        os.chdir(repo_path)

        # Create client and conversation with system prompt
        client = setup_client()
        conversation_id = client.create_conversation(system_prompt=system_prompt)

        # Configure Git user info
        logger.info("Configuring Git user information")
        repo = Repo(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", os.environ["GITHUB_USERNAME"])
            config.set_value(
                "user",
                "email",
                f"{os.environ['GITHUB_USERNAME']}@users.noreply.github.com",
            )

        # Create branch
        setup_prompt = PROMPTS["setup_repository"].format(todo=todo)
        logger.debug(f"Setup prompt: {setup_prompt}")
        branch_response = client.send_message(
            setup_prompt,
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
            logger.info(
                f"Implementation attempt {attempt + 1}/{max_implementation_attempts}"
            )

            # Get the list of files
            files = get_file_list(repo_path)
            logger.info(f"Found {len(files)} files")
            files_directory = PROMPTS["files"].format(files=", ".join(map(str, files)))

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

            logger.debug(f"Execute todo prompt: {execute_todo_prompt}")
            execute_todo_response = client.send_message(
                execute_todo_prompt,
                conversation_id=conversation_id,
            )
            handle_tool_response(client, execute_todo_response)

            # Validate acceptance criteria
            is_valid, validation_message = validate_acceptance_criteria(
                client, conversation_id, repo_path, todo, acceptance_criteria
            )

            if is_valid:
                logger.info("All acceptance criteria met, proceeding to create PR")
                break

            if attempt == max_implementation_attempts - 1:
                logger.error(
                    f"Failed to meet acceptance criteria after {max_implementation_attempts} attempts. "
                    f"Last validation message: {validation_message}"
                )
                return None

            logger.warning(
                f"Acceptance criteria not met (attempt {attempt + 1}): {validation_message}"
            )
            time.sleep(5)  # Brief pause before retry

        # Create PR with retries
        max_retries = 3
        for attempt in range(max_retries):
            create_pr_prompt = PROMPTS["create_pr"].format(
                repo_full_name=f"{repo_owner}/{repo_name}",
                head=branch_name,
                base="main",
                todo=todo,
                acceptance_criteria=acceptance_criteria,
            )
            logger.debug(f"Create PR prompt: {create_pr_prompt}")
            pr_response = client.send_message(
                create_pr_prompt,
                tool_choice={"type": "tool", "name": "create_pull_request"},
            )

            pr_result = handle_tool_response(client, pr_response)

            logger.debug(f"PR result: {pr_result}")

            if pr_result.get("success"):
                return pr_result.get("pr_url")
            else:
                logger.warning(
                    f"PR creation attempt {attempt+1} failed: {pr_result.get('error')}"
                )
                if attempt < max_retries - 1:
                    logger.info("Retrying PR creation...")
                    time.sleep(5)

        logger.error(f"PR creation failed after {max_retries} attempts")
        return None

    except Exception as e:
        logger.error(f"Error in todo_to_pr: {str(e)}", exc_info=True)
        raise

    finally:
        os.chdir(original_dir)  # Restore original directory


if __name__ == "__main__":
    todos_path = (
        Path(__file__).parent.parent.parent.parent.parent / "data" / "todos.csv"
    )

    with open(todos_path, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for i, row in enumerate(reader):
            if len(row) >= 2:
                todo, acceptance_criteria = row[0], row[1]
                todo_to_pr(
                    todo=todo.strip(),
                    repo_owner="koii-network",
                    repo_name="builder-test",
                    acceptance_criteria=acceptance_criteria.strip(),
                    repo_path=f"./repo_{i}",  # Unique path per task
                    system_prompt=os.environ["SYSTEM_PROMPT"],
                )
            else:
                print(f"Skipping invalid row: {row}")
