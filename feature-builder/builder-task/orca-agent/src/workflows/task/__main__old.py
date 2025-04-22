import sys
import csv
import json
import argparse
import os
import uuid
from github import Github, GithubException
from src.workflows.task.workflow import TaskWorkflow
from prometheus_swarm.utils.logging import (
    log_section,
    log_key_value,
    configure_logging,
)
from src.database import get_db, Log
from src.clients import setup_client
from src.workflows.utils import create_remote_branch
from src.workflows.task.prompts import PROMPTS
from src.utils.test_signatures import create_test_signatures
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def generate_test_task_id():
    """Generate a unique task ID for testing.
    Format: uuid4_short
    """
    return str(uuid.uuid4())[:8]


def run_workflow(source_repo_url, todo, acceptance_criteria):
    """Run task workflow on GitHub repository.

    Args:
        source_repo_url: URL of the source repository (fork) to create PRs to
        todo: Todo task description
        acceptance_criteria: List of acceptance criteria
    """
    # Check for required environment variables
    required_env_vars = [
        "LEADER_GITHUB_TOKEN",
        "LEADER_GITHUB_USERNAME",
        "WORKER_GITHUB_TOKEN",
        "WORKER_GITHUB_USERNAME",
    ]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_vars:
        print(
            f"Error: Missing required environment variables: {', '.join(missing_vars)}"
        )
        sys.exit(1)

    client = setup_client("anthropic")

    # Generate unique test values
    test_task_id = generate_test_task_id()
    test_round_number = 1

    # Parse source repo URL
    parts = source_repo_url.strip("/").split("/")
    if len(parts) < 5 or parts[2] != "github.com":
        print("Invalid repository URL format. Use https://github.com/owner/repo")
        sys.exit(1)
    source_owner, source_repo = parts[-2:]

    # 1. Get or create leader's fork from source repo
    leader_gh = Github(os.environ["LEADER_GITHUB_TOKEN"])
    source = leader_gh.get_repo(f"{source_owner}/{source_repo}")
    leader_user = leader_gh.get_user()

    try:
        leader_fork = leader_gh.get_repo(f"{leader_user.login}/{source_repo}")
        log_key_value("Using existing leader fork", leader_fork.html_url)
    except GithubException:
        # Create new fork from source
        leader_fork = leader_user.create_fork(source)
        log_key_value("Created leader fork", leader_fork.html_url)

    # Create unique base branch on leader's fork
    base_branch = f"task-{test_task_id}-round-{test_round_number}"
    create_result = create_remote_branch(
        repo_owner=leader_user.login,
        repo_name=source_repo,
        branch_name=base_branch,
        github_token=os.environ["LEADER_GITHUB_TOKEN"],
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

    # Run workflow as worker, creating PRs to leader's fork
    workflow = TaskWorkflow(
        client=client,
        prompts=PROMPTS,
        repo_owner=leader_user.login,
        repo_name=source_repo,
        todo=todo,
        acceptance_criteria=acceptance_criteria,
        staking_key=signatures["staking_key"],
        pub_key=signatures["pub_key"],
        staking_signature=signatures["staking_signature"],
        public_signature=signatures["public_signature"],
        round_number=test_round_number,
        task_id=test_task_id,
        base_branch=base_branch,
        github_token="WORKER_GITHUB_TOKEN",
        github_username="WORKER_GITHUB_USERNAME",
    )

    workflow.run()


def parse_repo_url(url: str) -> tuple[str, str]:
    """Parse a GitHub repository URL into owner and repo name.

    Args:
        url (str): GitHub repository URL

    Returns:
        tuple[str, str]: (owner, repo_name)
    """
    # Remove .git suffix if present
    if url.endswith(".git"):
        url = url[:-4]

    # Remove protocol and github.com
    url = url.replace("https://github.com/", "")
    url = url.replace("git@github.com:", "")

    # Split into owner/repo
    parts = url.split("/")
    return parts[-2], parts[-1]


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Run task workflow on GitHub repository"
    )
    parser.add_argument(
        "--repo",
        type=str,
        required=True,
        help="GitHub repository URL to create PRs to (e.g., https://github.com/owner/repo)",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Path to CSV file containing todos and acceptance criteria",
        default="test_todos_small.csv",
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

    # Get data directory from environment
    data_dir = os.environ.get("DATA_DIR")
    if not data_dir:
        raise ValueError("DATA_DIR environment variable must be set")

    todos_file = os.path.join(data_dir, args.input)

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
                            source_repo_url=args.repo,
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
