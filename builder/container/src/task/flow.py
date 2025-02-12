# Standard library imports
import os
import sys
from datetime import datetime
import time
from pathlib import Path
import csv
import shutil
import traceback
from git import Repo

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


def handle_tool_response(client, response, tool_choice={"type": "any"}):
    """
    Handle tool responses recursively until natural completion.
    """
    print("Start Conversation")
    final_output = None

    while response.stop_reason == "tool_use":
        # Process all tool uses in the current response
        for tool_use in [b for b in response.content if isinstance(b, ToolUseBlock)]:
            print(f"Processing tool: {tool_use.name}")
            print(f"Tool input: {tool_use.input}")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Execute the tool
            tool_output = client.execute_tool(tool_use)
            print(f"Tool output: {tool_output}")

            # Send tool result back to AI
            response = client.send_message(
                tool_response=str(tool_output),
                tool_use_id=tool_use.id,
                conversation_id=response.conversation_id,
                tool_choice=tool_choice,
            )

            # Store final output if we have a text response
            if response.stop_reason != "tool_use":
                final_output = response.content[0].text if response.content else ""

    print("End Conversation")
    return final_output or "Task completed successfully"


def todo_to_pr(
    repo_owner,
    repo_name,
    todo,
    acceptance_criteria,
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

        client = setup_client()

        # Configure Git user info
        print("Configuring Git user information")
        repo = Repo(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", os.environ["GITHUB_USERNAME"])
            config.set_value(
                "user",
                "email",
                f"{os.environ['GITHUB_USERNAME']}@users.noreply.github.com",
            )

        # Create a feature branch
        setup_repository_prompt = PROMPTS["setup_repository"].format(
            repo_path=repo_path, todo=todo
        )
        print("Setup repository prompt: ", setup_repository_prompt)
        createBranchResponse = client.send_message(setup_repository_prompt)
        time.sleep(10)
        print("Create branch response: ", createBranchResponse)
        handle_tool_response(client, createBranchResponse)
        branch_info = get_current_branch()
        print("Branch info: ", branch_info)
        branch_name = branch_info.get("output") if branch_info.get("success") else None
        print("Using Branch: ", branch_name)
        # Get the list of files
        files = get_file_list(repo_path)
        print("Use Files: ", files)
        files_directory = PROMPTS["files"].format(files=", ".join(map(str, files)))
        execute_todo_response = client.send_message(
            f"{todo}. Your solution must meet the following criteria: {acceptance_criteria}{files_directory}"
        )
        time.sleep(10)
        handle_tool_response(client, execute_todo_response)

        time.sleep(10)
        commit_response = client.send_message(
            PROMPTS["commit"].format(todo=todo),
            tool_choice={"type": "tool", "name": "make_commit"},
        )
        handle_tool_response(client, commit_response)

        # Single push operation
        push_response = client.send_message(
            PROMPTS["push"],
            tool_choice={"type": "tool", "name": "push_remote"},
        )
        handle_tool_response(client, push_response)

        # Create PR
        pr_response = client.send_message(
            PROMPTS["create_pr"].format(
                repo_full_name=f"{repo_owner}/{repo_name}",
                head=f"{os.environ['GITHUB_USERNAME']}:{branch_name}",
                base="main",
                todo=todo,
                acceptance_criteria=acceptance_criteria,
            ),
            tool_choice={"type": "tool", "name": "create_pull_request"},
        )

        # Handle PR creation once
        pr_result = handle_tool_response(client, pr_response)

        if pr_result.get("success"):
            return pr_result.get("pr_url")
        else:
            return f"PR creation failed: {pr_result.get('error')}"

    except Exception as e:
        print(f"\n{' ERROR '.center(50, '=')}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"Repo Path: {repo_path}")
        traceback.print_exc()
        print("=" * 50)

    finally:
        os.chdir(original_dir)  # Restore original directory


if __name__ == "__main__":
    todos_path = Path(__file__).parent / "data" / "todos.csv"

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
                )
            else:
                print(f"Skipping invalid row: {row}")
