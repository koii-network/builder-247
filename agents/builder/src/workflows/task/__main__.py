import sys
from pathlib import Path
import csv
import json
import argparse
import os
from src.workflows.task.workflow import TaskWorkflow
from src.utils.logging import (
    log_section,
    log_key_value,
    configure_logging,
)
from src.database import get_db, Log
from src.clients import setup_client
from src.workflows.prompts import TASK_PROMPTS


def run_workflow(repo_owner, repo_name, todo, acceptance_criteria):
    client = setup_client("anthropic")
    workflow = TaskWorkflow(
        client=client,
        prompts=TASK_PROMPTS,
        repo_owner=repo_owner,
        repo_name=repo_name,
        todo=todo,
        acceptance_criteria=acceptance_criteria,
    )
    workflow.run()


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Run task workflow on GitHub repository"
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="GitHub repository URL (e.g., https://github.com/owner/repo)",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Path to CSV file containing todos and acceptance criteria",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic",
        choices=["anthropic", "openai", "xai"],
        help="Model provider to use (default: anthropic)",
    )
    args = parser.parse_args()

    # Set up logging
    configure_logging()

    # Parse repository URL to get owner and name
    repo_owner = None
    repo_name = None

    if args.repo:
        # Extract owner and name from URL
        # Format: https://github.com/owner/repo
        parts = args.repo.strip("/").split("/")
        if len(parts) >= 4 and parts[2] == "github.com":
            repo_owner = parts[3]
            repo_name = parts[4] if len(parts) > 4 else None

    # If repo owner or name is missing, use defaults
    if not repo_owner:
        repo_owner = "koii-network"
    if not repo_name:
        repo_name = "builder-test"

    # Determine CSV file path
    todos_path = Path(__file__).parent.parent.parent.parent.parent.parent / "data"

    if args.input:
        todos_file = todos_path / args.input
    else:
        todos_file = todos_path / "test_todos.csv"

    if not os.path.exists(todos_file):
        db = get_db()
        log = Log(level="ERROR", message=f"Todos file not found at {todos_file}")
        db.add(log)
        db.commit()
        print(f"Error: Todos file not found at {todos_file}")
        sys.exit(1)

    try:
        with open(todos_file, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for i, row in enumerate(reader):
                if len(row) >= 2:
                    todo, acceptance_criteria = row[0], row[1]
                    try:
                        log_section(f"PROCESSING TODO {i}")
                        run_workflow(
                            repo_owner=repo_owner,
                            repo_name=repo_name,
                            todo=todo.strip(),
                            acceptance_criteria=acceptance_criteria.strip(),
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
                        print(f"Error processing todo {i}: {str(e)}")
                        sys.exit(1)
                else:
                    log_key_value("Skipping invalid row", row)
    except Exception as e:
        db = get_db()
        log = Log(level="ERROR", message=str(e))
        db.add(log)
        db.commit()
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
