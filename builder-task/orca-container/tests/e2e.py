import json
import argparse
import os
from pathlib import Path
from tests.setup import TestSetup
from tests.data import DataManager
from pymongo import MongoClient
import uuid


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

    # Prepare the state dictionary
    state = {
        "step_completed": step_completed,
        "fork_url": data_manager.fork_url,
        "branch_name": data_manager.branch_name,
        "issue_uuid": data_manager.issue_uuid,
        "repo_owner": data_manager.repo_owner,
        "repo_name": data_manager.repo_name,
        "pr_urls": pr_urls,
        "round_number": data_manager.round_number,
    }

    # Save to file
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    print(f"\nState saved to {state_file} after completing step {step_completed}")


def load_state(data_manager, pr_urls, starting_step):
    """Load state from JSON file when skipping steps"""
    state_file = Path(__file__).parent / "e2e_state.json"

    if not state_file.exists():
        raise Exception(
            f"Cannot start from step {starting_step}: State file {state_file} does not exist"
        )

    with open(state_file, "r") as f:
        state = json.load(f)

    # Check if we have completed the previous step
    if state["step_completed"] < starting_step - 1:
        raise Exception(
            f"Cannot start from step {starting_step}: Previous step {starting_step - 1} has not been completed"
        )

    # Load state into data_manager
    data_manager.fork_url = state["fork_url"]
    data_manager.branch_name = state["branch_name"]
    data_manager.issue_uuid = state["issue_uuid"]
    data_manager.repo_owner = state["repo_owner"]
    data_manager.repo_name = state["repo_name"]

    # Load PR URLs
    pr_urls.update(state["pr_urls"])

    print(f"\nLoaded state from {state_file}")
    print(f"Starting from step {starting_step} with:")
    print(f"Fork URL: {data_manager.fork_url}")
    print(f"Branch name: {data_manager.branch_name}")
    print(f"Round number: {data_manager.round_number}")
    print(f"PR URLs: {pr_urls}")


def reset_mongodb():
    """Reset the MongoDB database by clearing collections and importing fresh test data"""
    print("\nResetting MongoDB database...")

    # Get data directory path - explicitly use tests/data
    data_dir = Path(__file__).parent / "data"
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
        # Verify connection and database exists
        client.server_info()
        print("Connected to MongoDB server")

        # Clear existing collections
        print("\nClearing existing collections...")
        result = db.issues.delete_many({})
        print(f"Cleared {result.deleted_count} issues")
        result = db.todos.delete_many({})
        print(f"Cleared {result.deleted_count} todos")
        result = db.systemprompts.delete_many({})
        print(f"Cleared {result.deleted_count} system prompts")
        # Also clear audits collection
        result = db.audits.delete_many({})
        print(f"Cleared {result.deleted_count} audits")

        # Read issues and todos first to build dependency mappings
        with open(issues_path, "r") as f:
            issues_data = json.load(f)
        with open(todos_path, "r") as f:
            todos_data = json.load(f)

        # Create UUID mappings
        title_to_uuid = {}
        issue_uuids = {}

        # Process issues first
        for issue in issues_data:
            real_uuid = str(uuid.uuid4())
            issue_uuids[issue["issueUuid"]] = real_uuid
            issue["issueUuid"] = real_uuid

        # First pass: generate UUIDs for all todos
        for todo in todos_data:
            todo_uuid = str(uuid.uuid4())
            todo["uuid"] = todo_uuid
            title_to_uuid[todo["title"]] = todo_uuid
            # Update issue UUID reference
            todo["issueUuid"] = issue_uuids[todo["issueUuid"]]

        # Second pass: update dependencies to use UUIDs
        for todo in todos_data:
            if "dependencies" in todo:
                todo["dependencies"] = [
                    title_to_uuid[dep_title] for dep_title in todo["dependencies"]
                ]

        # Now insert the processed data
        print("\nInserting issues...")
        result = db.issues.insert_many(issues_data)
        print(f"Inserted {len(result.inserted_ids)} issues")

        print("\nInserting todos...")
        result = db.todos.insert_many(todos_data)
        print(f"Inserted {len(result.inserted_ids)} todos")

        # Read and import system prompts
        print(f"\nReading system prompts from {prompts_path}")
        with open(prompts_path, "r") as f:
            prompts_data = json.load(f)
            # Convert to array if it's a single object
            if not isinstance(prompts_data, list):
                prompts_data = [prompts_data]

            # Map each prompt to the correct document format for systemprompts collection
            for prompt in prompts_data:
                db.systemprompts.insert_one(
                    {"taskId": prompt["taskId"], "prompt": prompt["prompt"]}
                )
            print(f"Imported {len(prompts_data)} system prompts")

        # Verify final counts
        print("\nVerifying final counts...")
        issues_count = db.issues.count_documents({})
        todos_count = db.todos.count_documents({})
        prompts_count = db.systemprompts.count_documents({})
        audits_count = db.audits.count_documents({})
        print(f"Final issues count: {issues_count}")
        print(f"Final todos count: {todos_count}")
        print(f"Final prompts count: {prompts_count}")
        print(f"Final audits count: {audits_count}")

        print("\nMongoDB database reset completed successfully")
    except Exception as e:
        print(f"Error resetting MongoDB database: {e}")
        raise
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


def run_test_sequence(
    start_step: int = 1,
    stop_step: int = 6,
    reset: bool = False,
    task_id: str = "",
    round_number: int = 1,
):
    """Run the test sequence from start_step to stop_step (inclusive)"""
    if reset:
        # Reset SQLite databases
        reset_databases()

        # Reset MongoDB
        reset_mongodb()

        # Remove state file if it exists
        state_file = Path(__file__).parent / "e2e_state.json"
        if state_file.exists():
            print(f"Removing state file: {state_file}")
            os.remove(state_file)

    # Get task ID from environment if not provided
    if not task_id:
        task_id = os.getenv("TASK_ID")
        if not task_id:
            raise ValueError(
                "No task ID provided and TASK_ID environment variable not set"
            )

    print(f"Using task ID: {task_id}")
    print(f"Using round number: {round_number}")

    # Initialize data manager
    data_manager = DataManager(task_id=task_id, round_number=round_number)
    pr_urls = {}

    # Load state if starting from a later step
    if start_step > 1 and not reset:
        load_state(data_manager, pr_urls, start_step)

    # Use TestSetup as a context manager to ensure servers are started and stopped properly
    with TestSetup() as test_setup:
        # Continue running rounds until all work is completed
        while True:
            print(f"\n{'='*80}")
            print(f"Starting round {data_manager.round_number}")
            print(f"{'='*80}")

            # Run the test steps for this round
            if start_step <= 1 <= stop_step:
                log_step(1, "Create aggregator repo")
                test_setup.create_aggregator_repo(data_manager)
                save_state(data_manager, pr_urls, 1)

            if start_step <= 2 <= stop_step:
                log_step(2, "Run worker task")
                test_setup.run_worker_task(data_manager, pr_urls)
                save_state(data_manager, pr_urls, 2)

            if start_step <= 3 <= stop_step:
                log_step(3, "Run worker audit")
                test_setup.run_worker_audit(data_manager, pr_urls)
                save_state(data_manager, pr_urls, 3)

            if start_step <= 4 <= stop_step:
                log_step(4, "Run leader task")
                test_setup.run_leader_task(data_manager)
                save_state(data_manager, pr_urls, 4)

            if start_step <= 5 <= stop_step:
                log_step(5, "Run leader audit")
                test_setup.run_leader_audit(data_manager, pr_urls)
                save_state(data_manager, pr_urls, 5)

            if start_step <= 6 <= stop_step:
                log_step(6, "Run aggregator info")
                test_setup.run_aggregator_info(data_manager)
                save_state(data_manager, pr_urls, 6)

            # Check if there's more work to be done
            if not check_remaining_work():
                print(f"\nAll work completed after round {data_manager.round_number}!")
                break

            # Increment round number and continue
            data_manager.round_number += 1
            print(f"\nMoving to round {data_manager.round_number}...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the test sequence for the builder task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available steps:
  1. Create aggregator repo
  2. Worker tasks (Worker 1 and Worker 2)
  3. Cross audits (Worker 2 audits Worker 1, then Worker 1 audits Worker 2)
  4. Update audit results
  5. Leader task
  6. Leader audits

Example usage:
  # Run the full sequence
  python -m tests.e2e

  # Run only the audit update
  python -m tests.e2e --start 4 --stop 4

  # Run from worker tasks to leader task
  python -m tests.e2e --start 2 --stop 5

  # Reset databases and run specific steps
  python -m tests.e2e --start 2 --stop 5 --reset

  # Run with specific task ID and round number
  python -m tests.e2e --task-id 123abc --round 2
""",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Start step number (1-6)",
    )
    parser.add_argument(
        "--stop",
        type=int,
        default=6,
        help="Stop step number (1-6)",
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
        "--round",
        type=int,
        default=1,
        help="Round number to use (defaults to 1)",
    )
    args = parser.parse_args()

    # Validate step numbers
    if not (1 <= args.start <= 6 and 1 <= args.stop <= 6):
        print("Error: Step numbers must be between 1 and 6")
        exit(1)
    if args.start > args.stop:
        print("Error: Start step cannot be greater than stop step")
        exit(1)

    run_test_sequence(
        args.start, args.stop, args.reset, task_id=args.task_id, round_number=args.round
    )
