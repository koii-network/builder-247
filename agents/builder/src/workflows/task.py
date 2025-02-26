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
from typing import List
import json
import ast

from src.tools.file_operations.implementations import list_files
from src.clients import setup_client
from src.workflows.prompts import PROMPTS
from src.tools.github_operations.implementations import fork_repository
from src.utils.retry import send_message_with_retry
from src.utils.errors import ClientAPIError
from src.utils.logging import (
    log_section,
    log_key_value,
    log_error,
    configure_logging,
)
from src.types import MessageContent, ToolCallContent
from src.database import get_db, Log

# Ensure environment variables are loaded
dotenv.load_dotenv()

# Get database instance
db = get_db()


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
    If a tool has return_value=True, returns immediately after executing that tool.
    """
    return client.handle_tool_response(response)


def validate_acceptance_criteria(client, todo, acceptance_criteria):
    """
    Validate that all acceptance criteria are met, including passing tests.
    Returns tuple of (bool, str) indicating success/failure and reason for failure.
    """
    log_section("VALIDATING ACCEPTANCE CRITERIA")

    # Get the list of files
    files_result = list_files(os.getcwd())
    if not files_result["success"]:
        return False, f"Failed to get file list: {files_result['message']}"

    files = files_result["data"]["files"]
    files_directory = ", ".join(map(str, files))

    validation_prompt = PROMPTS["validate_criteria"].format(
        todo=todo,
        acceptance_criteria=acceptance_criteria,
        files_directory=files_directory,
    )

    # Start a new conversation for validation
    validation_conversation_id = client.create_conversation(system_prompt=None)
    response = send_message_with_retry(
        client,
        prompt=validation_prompt,
        conversation_id=validation_conversation_id,
    )

    validation_results = client.handle_tool_response(response)
    if not validation_results:
        return False, "Failed to get validation result"

    # Find the validate_implementation result
    try:
        # Look for the last validate_implementation result
        validation_result = None
        for result in validation_results:
            try:
                parsed = ast.literal_eval(result["response"])
                if isinstance(parsed, dict):
                    if not parsed.get("success", False):
                        # Tool execution failed
                        return False, parsed.get("error", "Tool execution failed")
                    if "validated" in parsed and "message" in parsed:
                        validation_result = parsed
            except (ValueError, SyntaxError, AttributeError):
                continue

        if validation_result is None:
            return False, "No validation result found in response"

        return validation_result["validated"], validation_result.get(
            "message", "No validation message provided"
        )
    except Exception as e:
        return False, f"Error processing validation result: {str(e)}"


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
            error = fork_result.get("error", "Unknown error")
            log_error(Exception(error), "Fork failed")
            raise Exception(error)

        # Enter repo directory
        os.chdir(repo_path)

        # Create client and conversation with system prompt
        client = setup_client("anthropic")
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
        branch_results = client.handle_tool_response(branch_response)
        if not branch_results:
            raise Exception("Failed to create branch: No response from tool")

        # Get branch name from the result
        branch_result = ast.literal_eval(branch_results[-1]["response"])
        if not branch_result.get("success"):
            error = branch_result.get("error", "Unknown error")
            log_error(Exception(error), "Branch creation failed")
            raise Exception(f"Failed to create branch: {error}")
        branch_name = branch_result.get("branch_name")

        # Start new conversation for implementation phase
        log_section("STARTING IMPLEMENTATION")
        conversation_id = client.create_conversation(system_prompt=system_prompt)

        # Implementation loop - try up to 3 times to meet all acceptance criteria
        max_implementation_attempts = 3
        validation_message = ""  # Initialize validation message
        for attempt in range(max_implementation_attempts):
            log_section(
                f"IMPLEMENTATION ATTEMPT {attempt + 1}/{max_implementation_attempts}"
            )

            # Get the list of files
            files_result = list_files(repo_path)
            if not files_result["success"]:
                raise Exception(f"Failed to get file list: {files_result['message']}")

            files = files_result["data"]["files"]
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
            client.handle_tool_response(execute_todo_response)

            # Validate acceptance criteria
            is_valid, validation_message = validate_acceptance_criteria(
                client, todo, acceptance_criteria
            )

            if is_valid:
                log_key_value(
                    "Validation", "All acceptance criteria met, proceeding to create PR"
                )
                break

            if attempt == max_implementation_attempts - 1:
                msg = f"Failed to meet acceptance criteria after {max_implementation_attempts} attempts"
                log_error(Exception(validation_message), msg)
                return None

            log_key_value(f"Validation attempt {attempt + 1}", validation_message)
            time.sleep(5)  # Brief pause before retry

        # Create PR with retries
        log_section("CREATING PULL REQUEST")

        # Get the list of files
        files_result = list_files(os.getcwd())
        if not files_result["success"]:
            raise Exception(f"Failed to get file list: {files_result['message']}")

        files = files_result["data"]["files"]
        files_directory = ", ".join(map(str, files))

        create_pr_prompt = PROMPTS["create_pr"].format(
            repo_full_name=f"{repo_owner}/{repo_name}",
            head=branch_name,
            base="main",
            todo=todo,
            acceptance_criteria=acceptance_criteria,
            files_directory=files_directory,
        )
        # Start a new conversation for PR creation
        pr_conversation_id = client.create_conversation(system_prompt=None)
        pr_response = send_message_with_retry(
            client, prompt=create_pr_prompt, conversation_id=pr_conversation_id
        )

        pr_results = client.handle_tool_response(pr_response)
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
        # Set up logging
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
            db = get_db()
            log = Log(level="ERROR", message=f"Todos file not found at {todos_path}")
            db.add(log)
            db.commit()
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
                        db = get_db()
                        log = Log(
                            level="ERROR",
                            message=str(e),
                            additional_data=json.dumps({"todo_index": i}),
                        )
                        db.add(log)
                        db.commit()
                        sys.exit(1)
                else:
                    log_key_value("Skipping invalid row", row)
    except Exception as e:
        db = get_db()
        log = Log(level="ERROR", message=str(e))
        db.add(log)
        db.commit()
        sys.exit(1)
