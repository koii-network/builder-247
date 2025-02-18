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
import dotenv

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


dotenv.load_dotenv()


def handle_tool_response(client, response, tool_choice={"type": "any"}):
    """
    Handle tool responses recursively until natural completion.
    """
    print("Start Conversation")
    tool_result = None  # Track the final tool execution result

    while response.stop_reason == "tool_use":
        # Process all tool uses in the current response
        for tool_use in [b for b in response.content if isinstance(b, ToolUseBlock)]:
            print(f"Processing tool: {tool_use.name}")
            print(f"Tool input: {tool_use.input}")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Execute the tool
            tool_output = client.execute_tool(tool_use)
            tool_result = tool_output  # Store the final tool result
            print(f"Tool output: {tool_output}")

            # Send tool result back to AI
            response = client.send_message(
                tool_response=str(tool_output),
                tool_use_id=tool_use.id,
                conversation_id=response.conversation_id,
                tool_choice=tool_choice,
            )

    print("End Conversation")
    return tool_result  # Return the final tool execution result


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
        print("Configuring Git user information")
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
        print("setup_prompt", setup_prompt)
        branch_response = client.send_message(
            setup_prompt,
            conversation_id=conversation_id,
            tool_choice={"type": "tool", "name": "create_branch"},
        )
        handle_tool_response(client, branch_response)
        branch_info = get_current_branch()
        branch_name = branch_info.get("output") if branch_info.get("success") else None

        # Get the list of files
        files = get_file_list(repo_path)
        print("Use Files: ", files)
        files_directory = PROMPTS["files"].format(files=", ".join(map(str, files)))
        execute_todo_prompt = PROMPTS["execute_todo"].format(
            todo=todo,
            files_directory=files_directory,
        )
        print("execute_todo_prompt", execute_todo_prompt)
        execute_todo_response = client.send_message(
            execute_todo_prompt,
            conversation_id=conversation_id,
        )
        time.sleep(10)
        handle_tool_response(client, execute_todo_response)

        time.sleep(10)

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
            print("create_pr_prompt", create_pr_prompt)
            pr_response = client.send_message(
                create_pr_prompt,
                tool_choice={"type": "tool", "name": "create_pull_request"},
            )

            pr_result = handle_tool_response(client, pr_response)

            print("pr_result", pr_result)

            if pr_result.get("success"):
                return pr_result.get("pr_url")
            else:
                print(
                    f"PR creation attempt {attempt+1} failed: {pr_result.get('error')}"
                )
                if attempt < max_retries - 1:
                    print("Retrying...")
                    time.sleep(5)

        print(f"PR creation failed after {max_retries} attempts")
        return None

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
