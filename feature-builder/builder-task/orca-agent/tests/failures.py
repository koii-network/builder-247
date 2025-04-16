import argparse
import os
from pathlib import Path
import requests
from tests.setup import TestSetup
from tests.data import DataManager
from tests.e2e import (
    log_request,
    log_response,
    log_step,
)
from pymongo import MongoClient
import uuid


def setup_test_data(task_id: str):
    """Set up minimal test data with one todo and one issue"""
    print("\nSetting up test data...")

    # Delete SQLite database files
    builder_path = Path(__file__).parent.parent
    for role in ["leader", "worker1", "worker2"]:
        db_path = builder_path / f"database_{role}.db"
        if db_path.exists():
            print(f"Deleting database file: {db_path}")
            os.remove(db_path)
            print(f"Deleted SQLite database: {db_path}")

    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongodb_uri)
    db = client["builder247"]

    try:
        # Clear existing data
        db.issues.delete_many({})
        db.todos.delete_many({})
        db.systemprompts.delete_many({})
        db.audits.delete_many({})

        # Create one issue with 'main' as the UUID
        issue_uuid = "main"  # Use main branch as the UUID
        issue = {
            "taskId": task_id,
            "issueUuid": issue_uuid,
            "uuid": issue_uuid,
            "status": "assign_pending",  # Issue ready for leader task
            "title": "Test Issue",
            "description": "Test issue for failure tests",
            "repoOwner": "koii-network",
            "repoName": "builder-test",
            "aggregatorOwner": "momstrosity",
        }
        db.issues.insert_one(issue)

        # Create one todo
        todo_uuid = str(uuid.uuid4())
        todo = {
            "taskId": task_id,
            "uuid": todo_uuid,
            "issueUuid": issue_uuid,  # Link to the 'main' issue
            "status": "initialized",  # Todo ready to be picked up
            "title": "Test Todo",
            "description": "Test todo for failure tests",
            "dependencyTasks": [],
            "repoOwner": "koii-network",
            "repoName": "builder-test",
            "acceptanceCriteria": ["Test criteria"],
        }
        db.todos.insert_one(todo)

        # Create system prompt
        system_prompt = {
            "taskId": task_id,
            "prompt": "Test system prompt for failure tests",
            "type": "default",
        }
        db.systemprompts.insert_one(system_prompt)

        print("Test data setup complete!")
        print(f"Created issue with UUID: {issue_uuid}")
        print(f"Created todo with UUID: {todo_uuid}")

    finally:
        client.close()


def simulate_worker_workflow_failure(test_setup, data_manager):
    """Simulate a worker task failure during workflow execution"""
    log_step("worker-workflow-failure", "Testing worker task workflow failure")

    # Get a valid payload with correct signatures
    payload = data_manager.prepare_worker_task("worker1", data_manager.round_number)

    # Try to run worker task - should fail during workflow execution
    url = f"{test_setup.worker1_server.url}/worker-task/{data_manager.round_number}"
    log_request("POST", url, payload)
    response = requests.post(url, json=payload)
    log_response(response)


def simulate_leader_workflow_failure(test_setup, data_manager):
    """Simulate a leader task failure during workflow execution"""
    log_step("leader-workflow-failure", "Testing leader task workflow failure")

    # Update issue status in MongoDB
    mongodb_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/builder247")
    client = MongoClient(mongodb_uri)
    db = client["builder247"]
    try:
        # Update the issue status to assign_pending
        db.issues.update_one(
            {"taskId": data_manager.task_id}, {"$set": {"status": "assign_pending"}}
        )
        print("Updated issue status to assign_pending")
    finally:
        client.close()

    # Get a valid payload with correct signatures
    payload = data_manager.prepare_leader_task("leader", data_manager.round_number)

    # Try to run leader task - should fail during workflow execution
    url = f"{test_setup.leader_server.url}/leader-task/{data_manager.round_number}"
    log_request("POST", url, payload)
    response = requests.post(url, json=payload)
    log_response(response)


def run_failure_simulations(test_setup, task_id: str = "", data_dir: Path = None):
    """Run all failure simulations"""
    # Get task ID from environment if not provided
    if not task_id:
        task_id = os.getenv("TASK_ID")
        if not task_id:
            raise ValueError(
                "No task ID provided and TASK_ID environment variable not set"
            )

    # Initialize data manager
    data_manager = DataManager(task_id=task_id)
    data_manager.round_number = 1  # Set round number for task failures

    # Set required fields on data manager (needed for payload preparation)
    data_manager.fork_url = "https://github.com/test-owner/test-repo"
    data_manager.branch_name = "test-branch"

    # Set up minimal test data
    setup_test_data(task_id)

    print(f"\nRunning failure simulations with task ID: {task_id}")

    print("\nTesting worker workflow failure...")
    simulate_worker_workflow_failure(test_setup, data_manager)

    print("\nTesting leader workflow failure...")
    simulate_leader_workflow_failure(test_setup, data_manager)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run workflow failure simulations for task failure recording functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  # Run simulations with default task ID from environment
  python -m tests.failures

  # Run with specific task ID
  python -m tests.failures --task-id 123abc

  # Run with custom data directory
  python -m tests.failures --data-dir /path/to/data
""",
    )
    parser.add_argument(
        "--task-id",
        type=str,
        help="Task ID to use (defaults to TASK_ID environment variable)",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Directory containing MongoDB data files",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else Path(os.getenv("DATA_DIR"))

    # Get task ID from environment if not provided
    task_id = args.task_id or os.getenv("TASK_ID")
    if not task_id:
        raise ValueError("No task ID provided and TASK_ID environment variable not set")

    print(f"Using task ID: {task_id}")

    # Set up test data before starting servers
    setup_test_data(task_id)

    # Use TestSetup as a context manager to ensure servers are started and stopped properly
    with TestSetup() as test_setup:
        # Initialize data manager
        data_manager = DataManager(task_id=task_id)
        data_manager.round_number = 1  # Set round number for task failures

        # Set required fields on data manager (needed for payload preparation)
        data_manager.fork_url = "https://github.com/test-owner/test-repo"
        data_manager.branch_name = "test-branch"

        print(f"\nRunning workflow failure simulations with task ID: {task_id}")

        print("\nTesting worker workflow failure...")
        simulate_worker_workflow_failure(test_setup, data_manager)

        print("\nTesting leader workflow failure...")
        simulate_leader_workflow_failure(test_setup, data_manager)
