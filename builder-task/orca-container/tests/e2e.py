import json
import argparse
import os
from pathlib import Path
from tests.setup import TestSetup
from tests.data import DataManager
from pymongo import MongoClient
import uuid
import requests


# Add this near the top of the file after imports
STEP_MAPPING = {
    "create-aggregator": 1,
    "worker1-task": 2,
    "worker2-task": 3,
    "worker1-submission": 4,
    "worker2-submission": 5,
    "worker1-audit": 6,
    "worker2-audit": 7,
    "worker-audit-results": 8,
    "leader-task": 9,
    "leader-submission": 10,
    "leader-audit": 11,
    "leader-audit-results": 12,
}


def log_request(method: str, url: str, payload: dict = None):
    """Log request details"""
    print("\n" + "=" * 80)
    print(f"REQUEST: {method} {url}")
    print("-" * 80)
    if payload:
        print("Payload:")
        print(json.dumps(payload, indent=2))
    print("-" * 80)


def log_response(response):
    """Log response details"""
    print("\nRESPONSE:")
    print("-" * 80)
    print(f"Status: {response.status_code}")
    try:
        print("Body:")
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print(f"Raw response: {response.text}")
    print("=" * 80)


def log_step(step_number: int, description: str):
    """Log a test step with clear formatting"""
    print("\n" + "#" * 80)
    print(f"STEP {step_number}: {description}")
    print("#" * 80)


def reset_databases():
    """Delete all database files before starting the test sequence"""
    builder_path = Path(__file__).parent.parent
    for role in ["leader", "worker1", "worker2"]:
        db_path = builder_path / f"database_{role}.db"
        if db_path.exists():
            print(f"Deleting database file: {db_path}")
            os.remove(db_path)


def save_state(data_manager, pr_urls, step_completed):
    """Save the current state to a JSON file after completing a step"""
    state_file = Path(__file__).parent / "e2e_state.json"

    # Load existing state if it exists
    all_rounds_state = {}
    if state_file.exists():
        with open(state_file, "r") as f:
            all_rounds_state = json.load(f)

    # Create state for current round
    current_round_state = {
        "step_completed": step_completed,
        "fork_url": data_manager.fork_url,
        "branch_name": data_manager.branch_name,
        "issue_uuid": data_manager.issue_uuid,
        "repo_owner": data_manager.repo_owner,
        "repo_name": data_manager.repo_name,
        "pr_urls": pr_urls.copy(),  # Make a copy to avoid reference issues
        "round_number": data_manager.round_number,
    }

    # Store state under the current round number
    round_key = str(data_manager.round_number)
    all_rounds_state[round_key] = current_round_state

    # Save to file
    with open(state_file, "w") as f:
        json.dump(all_rounds_state, f, indent=2)

    print(
        f"\nState saved to {state_file} after completing step {step_completed} in round {data_manager.round_number}"
    )


def load_state(data_manager, pr_urls, starting_step):
    """Load state from JSON file when skipping steps"""
    state_file = Path(__file__).parent / "e2e_state.json"

    if not state_file.exists():
        raise Exception(
            f"Cannot start from step {starting_step}: State file {state_file} does not exist"
        )

    with open(state_file, "r") as f:
        all_rounds_state = json.load(f)

    # Get state for current round
    round_key = str(data_manager.round_number)

    if round_key not in all_rounds_state:
        # If starting a new round, check if previous round was completed
        prev_round_key = str(data_manager.round_number - 1)
        if prev_round_key in all_rounds_state:
            prev_round_state = all_rounds_state[prev_round_key]
            if prev_round_state["step_completed"] < 7:  # 7 is the last step
                raise Exception(
                    f"Cannot start round {data_manager.round_number}: Previous round {data_manager.round_number - 1} "
                    f"has not been completed (stopped at step {prev_round_state['step_completed']})"
                )
            # Load state from previous round since it was completed
            current_round_state = prev_round_state
            # Save the loaded state back to the file
            all_rounds_state[round_key] = current_round_state
            with open(state_file, "w") as f:
                json.dump(all_rounds_state, f, indent=2)
        else:
            return  # New round, no state to load
    else:
        current_round_state = all_rounds_state[round_key]
        # If current round's values are null, try to get them from previous round
        if not current_round_state.get("fork_url") or not current_round_state.get(
            "branch_name"
        ):
            prev_round_key = str(data_manager.round_number - 1)
            if prev_round_key in all_rounds_state:
                prev_round_state = all_rounds_state[prev_round_key]
                if (
                    prev_round_state["step_completed"] == 7
                ):  # Previous round was completed
                    print(f"Using values from completed round {prev_round_key}")
                    # Only override null values
                    for key in [
                        "fork_url",
                        "branch_name",
                        "issue_uuid",
                        "repo_owner",
                        "repo_name",
                    ]:
                        if not current_round_state.get(key):
                            current_round_state[key] = prev_round_state.get(key)
                    # Save the updated state back to the file
                    with open(state_file, "w") as f:
                        json.dump(all_rounds_state, f, indent=2)

    # Check if we have completed the previous step
    if current_round_state["step_completed"] < starting_step - 1:
        raise Exception(
            f"Cannot start from step {starting_step} in round {data_manager.round_number}: "
            f"Previous step {starting_step - 1} has not been completed"
        )

    # Load state into data_manager
    data_manager.fork_url = current_round_state["fork_url"]
    data_manager.branch_name = current_round_state["branch_name"]
    data_manager.issue_uuid = current_round_state["issue_uuid"]
    data_manager.repo_owner = current_round_state["repo_owner"]
    data_manager.repo_name = current_round_state["repo_name"]

    # Load PR URLs for current round
    pr_urls.clear()  # Clear existing URLs
    pr_urls.update(current_round_state["pr_urls"])

    print(f"\nLoaded state from {state_file} for round {data_manager.round_number}")
    print(f"Starting from step {starting_step} with:")
    print(f"Fork URL: {data_manager.fork_url}")
    print(f"Branch name: {data_manager.branch_name}")
    print(f"Round number: {data_manager.round_number}")
    print(f"PR URLs: {pr_urls}")


def get_previous_round_prs(round_number: int) -> dict:
    """Get PR URLs from a previous round"""
    state_file = Path(__file__).parent / "e2e_state.json"
    if not state_file.exists():
        return {}

    with open(state_file, "r") as f:
        all_rounds_state = json.load(f)

    round_key = str(round_number)
    if round_key not in all_rounds_state:
        return {}

    return all_rounds_state[round_key].get("pr_urls", {})


def reset_mongodb(data_dir: Path = None, task_id: str = None):
    """Reset the MongoDB database by clearing collections and importing fresh test data"""
    print("\nResetting MongoDB database...")

    # Get data directory path - use provided path or default to tests/data
    if data_dir is None:
        data_dir = os.getenv("DATA_DIR")
    print(f"Using data directory: {data_dir}")

    # Check if files exist
    issues_path = data_dir / "issues.json"
    todos_path = data_dir / "todos.json"
    prompts_path = data_dir / "prompts.json"

    if not issues_path.exists():
        print(f"Error: issues.json not found at {issues_path}")
        return
    if not todos_path.exists():
        print(f"Error: todos.json not found at {todos_path}")
        return
    if not prompts_path.exists():
        print(f"Error: prompts.json not found at {prompts_path}")
        return

    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/todos")
    print(f"Connecting to MongoDB at: {mongodb_uri}")

    client = MongoClient(mongodb_uri)
    db = client["todos"]

    try:
        # Clear collections
        print("\nClearing collections...")
        db.issues.delete_many({})
        db.todos.delete_many({})
        db.systemprompts.delete_many({})
        db.audits.delete_many({})

        # Read and import issues
        print(f"\nReading issues from {issues_path}")
        with open(issues_path, "r") as f:
            issues_data = json.load(f)
            # Convert to array if it's a single object
            if not isinstance(issues_data, list):
                issues_data = [issues_data]

            # Replace task ID if provided
            if task_id:
                for issue in issues_data:
                    issue["taskId"] = task_id
                print(f"Set task ID to {task_id} for all issues")

            # Add UUIDs to issues and create mapping
            issue_uuid_mapping = {}
            for issue in issues_data:
                # Generate a new UUID for the issue
                new_uuid = str(uuid.uuid4())
                # Map the original issueUuid to the new UUID
                issue_uuid_mapping[issue["issueUuid"]] = new_uuid
                # Update the issue with the new UUID
                issue["issueUuid"] = new_uuid
                issue["uuid"] = new_uuid

            result = db.issues.insert_many(issues_data)
            print(f"Inserted {len(result.inserted_ids)} issues")

        # Read and import todos
        print(f"\nReading todos from {todos_path}")
        with open(todos_path, "r") as f:
            todos_data = json.load(f)
            # Convert to array if it's a single object
            if not isinstance(todos_data, list):
                todos_data = [todos_data]

            # Replace task ID if provided
            if task_id:
                for todo in todos_data:
                    todo["taskId"] = task_id
                print(f"Set task ID to {task_id} for all todos")

            # Update issue UUIDs in todos and add UUIDs to todos
            for todo in todos_data:
                if todo["issueUuid"] in issue_uuid_mapping:
                    # Update the todo's issueUuid to match the new issue UUID
                    todo["issueUuid"] = issue_uuid_mapping[todo["issueUuid"]]
                # Add UUID to each todo
                todo["uuid"] = str(uuid.uuid4())

            result = db.todos.insert_many(todos_data)
            print(f"Inserted {len(result.inserted_ids)} todos")

        # Read and import prompts
        print(f"\nReading prompts from {prompts_path}")
        with open(prompts_path, "r") as f:
            prompts_data = json.load(f)
            # Convert to array if it's a single object
            if not isinstance(prompts_data, list):
                prompts_data = [prompts_data]

            # Replace task ID if provided
            if task_id:
                for prompt in prompts_data:
                    prompt["taskId"] = task_id
                print(f"Set task ID to {task_id} for all prompts")

            result = db.systemprompts.insert_many(prompts_data)
            print(f"Inserted {len(result.inserted_ids)} prompts")

        print("\nMongoDB database reset complete!")
    finally:
        client.close()


def check_remaining_work():
    """Check if there are any remaining issues or todos that need to be completed"""
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/todos")
    client = MongoClient(mongodb_uri)
    db = client["todos"]

    try:
        # Check for unapproved todos
        pending_todos = db.todos.count_documents({"status": {"$ne": "approved"}})

        # Check for unapproved issues
        pending_issues = db.issues.count_documents({"status": {"$ne": "approved"}})

        print("\nRemaining work status:")
        print(f"Pending todos: {pending_todos}")
        print(f"Pending issues: {pending_issues}")

        return pending_todos > 0 or pending_issues > 0
    finally:
        client.close()


def determine_start_step(round_number: int, start_label: str = None) -> int:
    """Determine which step to start from based on saved state or provided label"""
    if start_label:
        if start_label not in STEP_MAPPING:
            raise ValueError(
                f"Unknown step label: {start_label}. Valid labels are: {', '.join(STEP_MAPPING.keys())}"
            )
        return STEP_MAPPING[start_label]

    state_file = Path(__file__).parent / "e2e_state.json"
    if not state_file.exists():
        return 1

    try:
        with open(state_file, "r") as f:
            all_rounds_state = json.load(f)

        round_key = str(round_number)
        if round_key not in all_rounds_state:
            # Check if previous round was completed
            prev_round_key = str(round_number - 1)
            if prev_round_key in all_rounds_state:
                prev_round_state = all_rounds_state[prev_round_key]
                if prev_round_state["step_completed"] < 12:  # Last step
                    raise Exception(
                        f"Cannot start round {round_number}: Previous round {round_number - 1} "
                        f"has not been completed (stopped at step {prev_round_state['step_completed']})"
                    )
            return 1  # Start new round from beginning

        # Resume from the next step after the last completed one
        current_round_state = all_rounds_state[round_key]
        return current_round_state["step_completed"] + 1
    except Exception as e:
        print(f"Error reading state file: {e}")
        return 1


def determine_current_round() -> int:
    """Determine the current round number from state file"""
    state_file = Path(__file__).parent / "e2e_state.json"
    if not state_file.exists():
        return 1

    try:
        with open(state_file, "r") as f:
            all_rounds_state = json.load(f)

        # Find the highest round number that exists
        max_round = 0
        for round_key in all_rounds_state:
            round_num = int(round_key)
            if round_num > max_round:
                max_round = round_num

        # Check if the highest round is completed
        if max_round > 0:
            last_round_state = all_rounds_state[str(max_round)]
            if last_round_state["step_completed"] == 7:  # Last step completed
                return max_round + 1
            return max_round  # Continue with current round

        return 1  # No rounds exist yet
    except Exception as e:
        print(f"Error reading state file: {e}")
        return 1


def check_and_populate_db(data_dir: Path = None, task_id: str = None):
    """Check if MongoDB collections are empty and populate them if needed"""
    print("\nChecking MongoDB collections...")

    mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/todos")
    client = MongoClient(mongodb_uri)
    db = client["todos"]

    try:
        # Check if required collections are empty (excluding audits)
        issues_count = db.issues.count_documents({})
        todos_count = db.todos.count_documents({})
        prompts_count = db.systemprompts.count_documents({})

        print("Current collection counts (required collections):")
        print(f"Issues: {issues_count}")
        print(f"Todos: {todos_count}")
        print(f"System Prompts: {prompts_count}")

        # Only check required collections (issues, todos, systemprompts)
        if issues_count == 0 or todos_count == 0 or prompts_count == 0:
            print(
                "\nOne or more required collections are empty. Populating database..."
            )
            reset_mongodb(data_dir, task_id)
            return True

        print("\nAll required collections have data. Proceeding...")
        return False
    finally:
        client.close()


def run_test_sequence(
    reset: bool = False,
    task_id: str = "",
    data_dir: Path = None,
    start_label: str = None,
):
    """Run the test sequence, automatically determining where to resume from"""
    if reset:
        # Reset SQLite databases
        reset_databases()

        # Reset MongoDB
        reset_mongodb(data_dir, task_id)

        # Remove state file if it exists
        state_file = Path(__file__).parent / "e2e_state.json"
        if state_file.exists():
            print(f"Removing state file: {state_file}")
            os.remove(state_file)
    else:
        # Check if database needs to be populated
        check_and_populate_db(data_dir, task_id)

    # Get task ID from environment if not provided
    if not task_id:
        task_id = os.getenv("TASK_ID")
        if not task_id:
            raise ValueError(
                "No task ID provided and TASK_ID environment variable not set"
            )

    # Determine current round from state
    round_number = determine_current_round()

    print(f"Using task ID: {task_id}")
    print(f"Starting with round {round_number}")

    # Initialize data manager
    data_manager = DataManager(task_id=task_id, round_number=round_number)
    pr_urls = {}
    submission_data = {}  # Store submission data for audits

    # Determine which step to start from
    start_step = determine_start_step(round_number, start_label)
    print(f"Resuming from step {start_step}")

    # Load state if we're not starting from the beginning
    if start_step > 1:
        load_state(data_manager, pr_urls, start_step)

    # Use TestSetup as a context manager to ensure servers are started and stopped properly
    with TestSetup() as test_setup:
        # Continue running rounds until all work is completed
        while True:
            print(f"\n{'='*80}")
            print(f"Starting round {data_manager.round_number}")
            print(f"{'='*80}")

            # Run the test steps for this round
            if start_step <= 1:
                log_step(1, "Create aggregator repo")
                test_setup.create_aggregator_repo(data_manager)
                save_state(data_manager, pr_urls, 1)

            if start_step <= 2:
                log_step(2, "Run worker1 task")
                test_setup.run_worker_task(data_manager, pr_urls, "worker1")
                save_state(data_manager, pr_urls, 2)

            if start_step <= 3:
                log_step(3, "Run worker2 task")
                test_setup.run_worker_task(data_manager, pr_urls, "worker2")
                save_state(data_manager, pr_urls, 3)

            if start_step <= 4:
                log_step(4, "Get worker1 submission")
                if "worker1" in pr_urls:
                    submission_url = f"{test_setup.worker1_url}/submission"
                    submission_params = {
                        "task_id": data_manager.task_id,
                        "round_number": data_manager.round_number,
                        "pr_url": pr_urls["worker1"],
                    }
                    log_request("GET", submission_url, submission_params)
                    response = requests.get(submission_url, params=submission_params)
                    log_response(response)
                    response.raise_for_status()
                    submission_data["worker1"] = response.json()
                save_state(data_manager, pr_urls, 4)

            if start_step <= 5:
                log_step(5, "Get worker2 submission")
                if "worker2" in pr_urls:
                    submission_url = f"{test_setup.worker2_url}/submission"
                    submission_params = {
                        "task_id": data_manager.task_id,
                        "round_number": data_manager.round_number,
                        "pr_url": pr_urls["worker2"],
                    }
                    log_request("GET", submission_url, submission_params)
                    response = requests.get(submission_url, params=submission_params)
                    log_response(response)
                    response.raise_for_status()
                    submission_data["worker2"] = response.json()
                save_state(data_manager, pr_urls, 5)

            if start_step <= 6:
                log_step(6, "Worker1 audits Worker2")
                test_setup.run_worker_audit(
                    data_manager, pr_urls, submission_data, "worker1", "worker2"
                )
                save_state(data_manager, pr_urls, 6)

            if start_step <= 7:
                log_step(7, "Worker2 audits Worker1")
                test_setup.run_worker_audit(
                    data_manager, pr_urls, submission_data, "worker2", "worker1"
                )
                save_state(data_manager, pr_urls, 7)

            if start_step <= 8:
                log_step(8, "Update worker audit results")
                test_setup.update_audit_results(data_manager, "worker")
                save_state(data_manager, pr_urls, 8)

            if start_step <= 9:
                log_step(9, "Run leader task")
                test_setup.run_leader_task(data_manager, pr_urls)
                save_state(data_manager, pr_urls, 9)

            if start_step <= 10:
                log_step(10, "Get leader submission")
                if "leader" in pr_urls:
                    submission_url = f"{test_setup.leader_url}/submission"
                    submission_params = {
                        "task_id": data_manager.task_id,
                        "round_number": data_manager.round_number,
                        "pr_url": pr_urls["leader"],
                    }
                    log_request("GET", submission_url, submission_params)
                    response = requests.get(submission_url, params=submission_params)
                    log_response(response)
                    response.raise_for_status()
                    submission_data["leader"] = response.json()
                save_state(data_manager, pr_urls, 10)

            if start_step <= 11:
                log_step(11, "Run leader audit")
                test_setup.run_leader_audit(data_manager, pr_urls, submission_data)
                save_state(data_manager, pr_urls, 11)

            if start_step <= 12:
                log_step(12, "Update leader audit results")
                test_setup.update_audit_results(data_manager, "leader")
                save_state(data_manager, pr_urls, 12)

            # Check if there's more work to be done
            if not check_remaining_work():
                print(f"\nAll work completed after round {data_manager.round_number}!")
                break

            # Increment round number and reset start_step for next round
            data_manager.round_number += 1
            start_step = 1  # Always start from beginning for new rounds
            print(f"\nMoving to round {data_manager.round_number}...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the test sequence for the builder task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The script will automatically determine where to resume from based on the saved state.
If no state exists, or if --reset is used, it will start from the beginning.
The current round is determined from the state file.

Available steps (use with --start-from):
  create-aggregator      - Create aggregator repo
  worker1-task          - Run worker1 task
  worker2-task          - Run worker2 task
  worker1-submission    - Get worker1 submission
  worker2-submission    - Get worker2 submission
  worker1-audit         - Worker1 audits Worker2
  worker2-audit         - Worker2 audits Worker1
  worker-audit-results  - Update worker audit results
  leader-task           - Run leader task
  leader-submission     - Get leader submission
  leader-audit          - Run leader audit
  leader-audit-results  - Update leader audit results

Example usage:
  # Run or resume the sequence
  python -m tests.e2e

  # Reset databases and start fresh
  python -m tests.e2e --reset

  # Start from a specific step
  python -m tests.e2e --start-from worker1-task

  # Run with specific task ID
  python -m tests.e2e --task-id 123abc

  # Run with custom data directory
  python -m tests.e2e --data-dir /path/to/data
""",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset SQLite databases, MongoDB, and state file before running",
    )
    parser.add_argument(
        "--task-id",
        type=str,
        help="Task ID to use (defaults to TASK_ID environment variable)",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Directory containing MongoDB data files (issues.json, todos.json, prompts.json)",
    )
    parser.add_argument(
        "--start-from",
        type=str,
        help="Label of the step to start from (see available steps below)",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else Path(os.getenv("DATA_DIR"))
    run_test_sequence(
        reset=args.reset,
        task_id=args.task_id,
        data_dir=data_dir,
        start_label=args.start_from,
    )
