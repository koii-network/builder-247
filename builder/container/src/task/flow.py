# Standard library imports
import os
import sys
from datetime import datetime
import time
from pathlib import Path
import csv
import shutil
import traceback

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
from src.task.setup import setup_repository, setup_client
from src.task.constants import PROMPTS


def handle_tool_response(
    client, response, tool_choice={"type": "any"}, max_iterations=10
):
    """
    Handle tool responses recursively until we get a text response.
    """
    print("Start Conversation")
    while response.stop_reason == "tool_use" and max_iterations > 0:
        tool_use = [block for block in response.content if block.type == "tool_use"][0]
        tool_name = tool_use.name
        tool_input = tool_use.input
        print("tool_name: " + tool_name)
        print("tool_input: " + str(tool_input))
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        tool_output = client.execute_tool(
            ToolUseBlock(
                id=tool_use.id, name=tool_name, input=tool_input, type="tool_use"
            )
        )
        print("tool_output: " + str(tool_output))

        # Ensure tool_output is a string
        if not isinstance(tool_output, str):
            tool_output_str = str(tool_output)
        time.sleep(10)

        response = client.send_message(
            tool_response=tool_output_str,
            tool_use_id=tool_use.id,
            conversation_id=response.conversation_id,
            tool_choice=tool_choice,
        )
        max_iterations -= 1
    print("End Conversation")
    return tool_output


def todo_to_pr(
    repo_owner,
    repo_name,
    todo,
    acceptance_criteria,
    repo_path=None,  # Make path parameter required
):
    """
    Task flow
    """

    # Generate unique repo path for each task
    safe_todo_name = "".join(c if c.isalnum() else "_" for c in todo)
    repo_path = repo_path or f"./repos/{safe_todo_name[:50]}"

    # Ensure clean working directory
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    # print("Using Directory:", os.getcwd())
    # print("Using path:", repo_path)
    client = setup_client(repo_path)
    # print("Client: ", client)
    try:
        # Set up the repository
        repo_path = setup_repository(repo_owner, repo_name, repo_path)
        print("Setup repository result: ", repo_path)
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

        github_username = os.environ.get("GITHUB_USERNAME")
        time.sleep(10)
        commit_response = client.send_message(
            PROMPTS["commit"].format(repo_path=repo_path, todo=todo),
            tool_choice={"type": "any"},
        )
        time.sleep(10)
        handle_tool_response(
            client, commit_response, tool_choice={"type": "tool", "name": "make_commit"}
        )
        time.sleep(10)
        push_response = client.send_message(
            PROMPTS["push"].format(repo_path=repo_path),
            tool_choice={"type": "tool", "name": "push_remote"},
        )
        time.sleep(10)
        handle_tool_response(
            client, push_response, tool_choice={"type": "tool", "name": "push_remote"}
        )
        time.sleep(10)
        create_pr_response = client.send_message(
            PROMPTS["create_pr"].format(
                repo_path=repo_path,
                todo=todo,
                repo_full_name=f"{repo_owner}/{repo_name}",
                head=f"{github_username}:{branch_name}",
                base="main",
            ),
            tool_choice={"type": "any"},
        )
        time.sleep(10)
        pr_result = handle_tool_response(
            client,
            create_pr_response,
            tool_choice={"type": "tool", "name": "create_pull_request"},
        )

        if isinstance(pr_result, str):
            return pr_result
        else:
            return pr_result.get("pr_url")

    except Exception as e:
        print(f"\n{' ERROR '.center(50, '=')}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"Repo Path: {repo_path}")
        traceback.print_exc()
        print("=" * 50)


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
