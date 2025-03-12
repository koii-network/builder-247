import sys
from pathlib import Path
import csv
import json
import argparse
import os
import uuid
from datetime import datetime
from src.workflows.task.workflow import TaskWorkflow
from src.utils.logging import (
    log_section,
    log_key_value,
    configure_logging,
)
from src.database import get_db, Log
from src.clients import setup_client
from src.workflows.task.prompts import PROMPTS
from src.utils.test_signatures import create_test_signatures
from src.workflows.utils import create_remote_branch


def generate_test_task_id():
    """Generate a unique task ID for testing.
    Format: test-{timestamp}-{uuid4_short}
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    return f"test-{timestamp}-{unique_id}"


def run_workflow(repo_owner, repo_name, todo, acceptance_criteria):
    # Check for required environment variables
    if not os.environ.get("UPSTREAM_GITHUB_TOKEN"):
        print(
            "Error: UPSTREAM_GITHUB_TOKEN environment variable is required for testing"
        )
        sys.exit(1)

    client = setup_client("anthropic")

    # Generate unique test values
    test_task_id = generate_test_task_id()
    test_round_number = 1

    # Create base branch on upstream repo
    base_branch = f"round-{test_round_number}-{test_task_id}"
    create_result = create_remote_branch(
        repo_owner=repo_owner,
        repo_name=repo_name,
        branch_name=base_branch,
        github_token=os.environ.get("UPSTREAM_GITHUB_TOKEN"),
    )
    if not create_result["success"]:
        error = create_result.get("error", "Unknown error")
        print(f"Error creating base branch: {error}")
        sys.exit(1)

    log_key_value("Created base branch", base_branch)

    # For testing, we'll create signatures using the keypairs from env vars
    staking_keypair_path = os.getenv("STAKING_KEYPAIR")
    public_keypair_path = os.getenv("PUBLIC_KEYPAIR")

    if staking_keypair_path and public_keypair_path:
        # Create test signatures
        payload = {
            "taskId": test_task_id,
            "roundNumber": test_round_number,
            "todo": todo,
            "acceptance_criteria": acceptance_criteria,
            "action": "task",
        }
        signatures = create_test_signatures(
            payload=payload,
            staking_keypair_path=staking_keypair_path,
            public_keypair_path=public_keypair_path,
        )
    else:
        # Use dummy values for testing without keypairs
        signatures = {
            "staking_key": "dummy_staking_key",
            "pub_key": "dummy_pub_key",
            "staking_signature": "dummy_staking_signature",
            "public_signature": "dummy_public_signature",
        }

    workflow = TaskWorkflow(
        client=client,
        prompts=PROMPTS,
        repo_owner=repo_owner,
        repo_name=repo_name,
        todo=todo,
        acceptance_criteria=acceptance_criteria,
        staking_key=signatures["staking_key"],
        pub_key=signatures["pub_key"],
        staking_signature=signatures["staking_signature"],
        public_signature=signatures["public_signature"],
        round_number=test_round_number,
        task_id=test_task_id,
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
        todos_file = todos_path / "test_todos_small.csv"

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
                    todo, acceptance_criteria_str = row[0], row[1]
                    # Parse acceptance criteria string into list
                    acceptance_criteria = [
                        criterion.strip()
                        for criterion in acceptance_criteria_str.split(";")
                        if criterion.strip()
                    ]
                    try:
                        log_section(f"PROCESSING TODO {i}")
                        run_workflow(
                            repo_owner=repo_owner,
                            repo_name=repo_name,
                            todo=todo.strip(),
                            acceptance_criteria=acceptance_criteria,
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
