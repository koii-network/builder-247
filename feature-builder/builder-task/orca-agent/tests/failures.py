import argparse
import os
from pathlib import Path
import requests
import time
import json
from tests.setup import TestSetup
from tests.data import DataManager
from tests.e2e import (
    log_request,
    log_response,
)
from pymongo import MongoClient
import uuid


def reset_databases():
    """Delete all database files before starting the test sequence"""
    builder_path = Path(__file__).parent.parent
    for role in ["leader", "worker1"]:
        db_path = builder_path / f"database_{role}.db"
        if db_path.exists():
            print(f"Deleting database file: {db_path}")
            os.remove(db_path)


def setup_test_data(task_id: str):
    """Set up minimal test data with one todo and one issue"""
    print("\nSetting up test data...")

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

        # Create one issue
        issue_uuid = str(uuid.uuid4())
        issue = {
            "taskId": task_id,
            "issueUuid": issue_uuid,
            "uuid": issue_uuid,
            "status": "initialized",
            "title": "Create a simple math utility function",
            "description": (
                "Create a Python function that performs basic arithmetic operations.\n\n"
                "The function should:\n"
                "1. Take two numbers and an operation as input\n"
                "2. Support addition, subtraction, multiplication, and division\n"
                "3. Handle division by zero errors\n"
                "4. Return the result of the operation"
            ),
            "repoOwner": "koii-network",
            "repoName": "builder-test",
            "aggregatorOwner": "momstrosity",
            "createdAt": time.time(),
            "updatedAt": time.time(),
        }
        db.issues.insert_one(issue)

        # Create one todo
        todo_uuid = str(uuid.uuid4())
        todo = {
            "taskId": task_id,
            "uuid": todo_uuid,
            "issueUuid": issue_uuid,
            "status": "initialized",
            "title": "Implement calculate function",
            "description": (
                "Create a calculate(a: float, b: float, operation: str) -> float function that:\n\n"
                "1. Takes two numbers (a, b) and operation as parameters\n"
                "2. Operation should be one of: '+', '-', '*', '/'\n"
                "3. Returns the result of a (operation) b\n"
                "4. Raises ValueError for invalid operations\n"
                "5. Handles division by zero appropriately"
            ),
            "dependencyTasks": [],
            "repoOwner": "koii-network",
            "repoName": "builder-test",
            "acceptanceCriteria": [
                "Function handles all basic operations correctly",
                "Division by zero is handled appropriately",
                "Invalid operations raise ValueError",
                "All parameters are properly type-hinted",
                "Function includes docstring with examples",
            ],
            "createdAt": time.time(),
            "updatedAt": time.time(),
        }
        db.todos.insert_one(todo)

        # Create system prompt
        system_prompt = {
            "taskId": task_id,
            "prompt": (
                "You are an AI coding assistant helping to implement a simple Python math utility.\n\n"
                "The calculate() function should:\n"
                "- Accept two numbers and an operation string\n"
                "- Support +, -, *, / operations\n"
                "- Include proper error handling\n"
                "- Use type hints and docstrings\n"
                "- Follow PEP 8 style guidelines"
            ),
            "type": "default",
            "createdAt": time.time(),
            "updatedAt": time.time(),
        }
        db.systemprompts.insert_one(system_prompt)

        print("Test data setup complete!")
        print(f"Created issue with UUID: {issue_uuid}")
        print(f"Created todo with UUID: {todo_uuid}")

        return issue_uuid, todo_uuid

    finally:
        client.close()


def save_state(data_manager, state_file: Path):
    """Save the current test state to a file"""
    state = {
        "task_id": data_manager.task_id,
        "round_number": data_manager.round_number,
        "fork_url": data_manager.fork_url,
        "branch_name": data_manager.branch_name,
        "issue_uuid": data_manager.issue_uuid,
        "pr_urls": data_manager.pr_urls,
        "submission_data": data_manager.submission_data,
        "last_completed_step": (
            data_manager.last_completed_step
            if hasattr(data_manager, "last_completed_step")
            else 0
        ),
    }

    state_file.parent.mkdir(parents=True, exist_ok=True)
    with state_file.open("w") as f:
        json.dump(state, f, indent=2)
    print(f"\nSaved state to {state_file}")


def load_state(state_file: Path) -> tuple[DataManager, int]:
    """Load test state from a file"""
    if not state_file.exists():
        return None, 0

    with state_file.open("r") as f:
        state = json.load(f)

    data_manager = DataManager(task_id=state["task_id"])
    data_manager.round_number = state["round_number"]
    data_manager.fork_url = state["fork_url"]
    data_manager.branch_name = state["branch_name"]
    data_manager.issue_uuid = state["issue_uuid"]
    data_manager.pr_urls = state["pr_urls"]
    data_manager.submission_data = state["submission_data"]
    data_manager.last_completed_step = state.get("last_completed_step", 0)

    print(f"\nLoaded state from {state_file}")
    print(f"Resuming from step {data_manager.last_completed_step + 1}")
    return data_manager, data_manager.last_completed_step


def run_failure_simulations(test_setup, task_id: str = "", data_dir: Path = None):
    """Run all failure simulations in the correct sequence"""
    # Determine state file location
    state_file = Path(__file__).parent / "test_state.json"

    # Try to load existing state
    loaded_data_manager, last_step = load_state(state_file)

    if loaded_data_manager:
        data_manager = loaded_data_manager
    else:
        if not task_id:
            task_id = os.getenv("TASK_ID")
            if not task_id:
                raise ValueError(
                    "No task ID provided and TASK_ID environment variable not set"
                )

        # Initialize data manager
        data_manager = DataManager(task_id=task_id)
        data_manager.round_number = 1
        data_manager.last_completed_step = 0

        # Set required fields on data manager
        data_manager.fork_url = "https://github.com/test-owner/test-repo"
        data_manager.branch_name = "test-branch"

        # Set up test data and get UUIDs
        issue_uuid, todo_uuid = setup_test_data(task_id)
        print(f"\nRunning failure simulations with task ID: {task_id}")

    # MongoDB connection for status updates
    mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongodb_uri)
    db = client["builder247"]

    try:
        # Define test steps as a list of tuples (step_number, description, function)
        steps = [
            (
                1,
                "Creating aggregator repo",
                lambda: test_setup.create_aggregator_repo(data_manager),
            ),
            (
                2,
                "Testing worker task failure",
                lambda: simulate_worker_task_failure(test_setup, data_manager, db),
            ),
            (
                3,
                "Running successful worker task",
                lambda: simulate_worker_task_success(test_setup, data_manager),
            ),
            (
                4,
                "Submitting worker task results",
                lambda: submit_worker_results(test_setup, data_manager),
            ),
            (
                5,
                "Testing worker audit failure",
                lambda: simulate_worker_audit_failure(test_setup, data_manager),
            ),
            (
                6,
                "Running successful worker audit",
                lambda: simulate_worker_audit_success(test_setup, data_manager),
            ),
            (
                7,
                "Updating worker audit results",
                lambda: test_setup.update_audit_results(data_manager, "worker"),
            ),
            (
                8,
                "Testing leader task failure",
                lambda: simulate_leader_task_failure(test_setup, data_manager),
            ),
            (
                9,
                "Running successful leader task",
                lambda: simulate_leader_task_success(test_setup, data_manager),
            ),
            (
                10,
                "Submitting leader task results",
                lambda: submit_leader_results(test_setup, data_manager),
            ),
            (
                11,
                "Testing leader audit failure",
                lambda: simulate_leader_audit_failure(test_setup, data_manager),
            ),
            (
                12,
                "Running successful leader audit",
                lambda: simulate_leader_audit_success(test_setup, data_manager),
            ),
            (
                13,
                "Updating leader audit results",
                lambda: test_setup.update_audit_results(data_manager, "leader"),
            ),
        ]

        # Execute steps starting from the last completed step
        for step_num, description, func in steps:
            if step_num <= data_manager.last_completed_step:
                print(f"\nSkipping step {step_num}: {description} (already completed)")
                continue

            print(f"\n{step_num}. {description}...")
            func()
            data_manager.last_completed_step = step_num
            save_state(data_manager, state_file)

    finally:
        client.close()
        # Ensure we reset force_failure at the end
        test_setup.set_force_failure(False)


def simulate_worker_task_failure(test_setup, data_manager, db):
    """Simulate worker task failure and reset todo status"""
    test_setup.set_force_failure(True)
    try:
        test_setup.run_worker_task(data_manager, "worker1")
    except Exception as e:
        print(f"Expected worker task failure: {e}")
        # Reset todo status back to initialized
        db.todos.update_one(
            {"taskId": data_manager.task_id}, {"$set": {"status": "initialized"}}
        )
        print("Reset todo status to initialized")
    data_manager.round_number += 1


def simulate_worker_task_success(test_setup, data_manager):
    """Run successful worker task"""
    test_setup.set_force_failure(False)
    test_setup.run_worker_task(data_manager, "worker1")


def submit_worker_results(test_setup, data_manager):
    """Submit worker task results"""
    if "worker1" in data_manager.pr_urls:
        submission_url = (
            f"{test_setup.worker1_server.url}/submission/"
            f"{data_manager.task_id}/{data_manager.round_number}"
        )
        log_request("GET", submission_url)
        response = requests.get(submission_url)
        log_response(response)
        response.raise_for_status()
        worker_data = response.json()

        # Get keys from DataManager
        keys = data_manager.get_keys("worker1")

        # Create signature for the submission
        submitter_payload = {
            "taskId": data_manager.task_id,
            "roundNumber": data_manager.round_number,
            "stakingKey": keys["staking_key"],
            "pubKey": keys["pub_key"],
            "action": "audit",
            "githubUsername": worker_data.get("githubUsername"),
            "prUrl": worker_data.get("prUrl"),
        }
        signature = data_manager.create_submitter_signature(
            "worker1", submitter_payload
        )
        worker_data["signature"] = signature
        # Add staking and pub keys to submission data
        worker_data["stakingKey"] = keys["staking_key"]
        worker_data["pubKey"] = keys["pub_key"]
        # Store worker's submission data
        data_manager.submission_data["worker1"] = worker_data


def simulate_worker_audit_failure(test_setup, data_manager):
    """Simulate worker audit failure"""
    test_setup.set_force_failure(True)
    try:
        test_setup.run_worker_audit(data_manager, "worker1", "worker1")
    except Exception as e:
        print(f"Expected worker audit failure: {e}")
    data_manager.round_number += 1


def simulate_worker_audit_success(test_setup, data_manager):
    """Run successful worker audit"""
    test_setup.set_force_failure(False)
    test_setup.run_worker_audit(data_manager, "worker1", "worker1")


def simulate_leader_task_failure(test_setup, data_manager):
    """Simulate leader task failure"""
    test_setup.set_force_failure(True)
    try:
        test_setup.run_leader_task(data_manager)
    except Exception as e:
        print(f"Expected leader task failure: {e}")
    data_manager.round_number += 1


def simulate_leader_task_success(test_setup, data_manager):
    """Run successful leader task"""
    test_setup.set_force_failure(False)
    test_setup.run_leader_task(data_manager)


def submit_leader_results(test_setup, data_manager):
    """Submit leader task results"""
    if "leader" in data_manager.pr_urls:
        submission_url = (
            f"{test_setup.leader_server.url}/submission/"
            f"{data_manager.task_id}/{data_manager.round_number}"
        )
        log_request("GET", submission_url)
        response = requests.get(submission_url)
        log_response(response)
        response.raise_for_status()
        leader_data = response.json()

        # Get keys from DataManager
        keys = data_manager.get_keys("leader")

        # Create signature for the submission
        submitter_payload = {
            "taskId": data_manager.task_id,
            "roundNumber": data_manager.round_number,
            "stakingKey": keys["staking_key"],
            "pubKey": keys["pub_key"],
            "action": "audit",
            "githubUsername": leader_data.get("githubUsername"),
            "prUrl": leader_data.get("prUrl"),
        }
        signature = data_manager.create_submitter_signature("leader", submitter_payload)
        leader_data["signature"] = signature
        # Add staking and pub keys to submission data
        leader_data["stakingKey"] = keys["staking_key"]
        leader_data["pubKey"] = keys["pub_key"]
        # Store leader's submission data
        data_manager.submission_data["leader"] = leader_data


def simulate_leader_audit_failure(test_setup, data_manager):
    """Simulate leader audit failure"""
    test_setup.set_force_failure(True)
    try:
        test_setup.run_leader_audit(data_manager)
    except Exception as e:
        print(f"Expected leader audit failure: {e}")
    data_manager.round_number += 1


def simulate_leader_audit_success(test_setup, data_manager):
    """Run successful leader audit"""
    test_setup.set_force_failure(False)
    test_setup.run_leader_audit(data_manager)


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
    task_id = args.task_id or os.getenv("TASK_ID")
    if not task_id:
        raise ValueError("No task ID provided and TASK_ID environment variable not set")

    print(f"Using task ID: {task_id}")

    # Reset databases before starting TestSetup
    reset_databases()
    setup_test_data(task_id)

    # Set initial state for first failure
    os.environ["FORCE_FAILURE"] = "true"

    with TestSetup() as test_setup:
        run_failure_simulations(test_setup, task_id, data_dir)
