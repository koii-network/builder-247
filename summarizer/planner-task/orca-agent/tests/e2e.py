import json
import argparse
import os
from pathlib import Path
from tests.setup import TestSetup
from tests.data import DataManager
from pymongo import MongoClient


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


def log_step(step_name: str, description: str):
    """Log a test step with clear formatting"""
    print("\n" + "#" * 80)
    print(f"STEP {step_name}: {description}")
    print("#" * 80)


def reset_databases():
    """Delete all database files before starting the test sequence"""
    builder_path = Path(__file__).parent.parent
    for role in ["leader", "worker1", "worker2"]:
        db_path = builder_path / f"database_{role}.db"
        if db_path.exists():
            print(f"Deleting database file: {db_path}")
            os.remove(db_path)


def save_state(data_manager, step_name):
    """Save the current state to a JSON file after completing a step"""
    state_file = Path(__file__).parent / "e2e_state.json"

    # Load existing state if it exists
    state = {}
    if state_file.exists():
        with open(state_file, "r") as f:
            state = json.load(f)

    # Ensure top-level structure exists
    if "task_id" not in state:
        state["task_id"] = data_manager.task_id
    if "issue_uuid" not in state:
        state["issue_uuid"] = data_manager.issue_uuid
    if "rounds" not in state:
        state["rounds"] = {}

    # Update current round data
    data_manager.last_completed_step = step_name
    round_key = str(data_manager.round_number)
    state["rounds"][round_key] = {
        "last_completed_step": data_manager.last_completed_step,
        "ipfs_cid": data_manager.ipfs_cid,
        "submission_data": data_manager.submission_data,
    }

    # Save to file
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    print(
        f"\nState saved to {state_file} after completing step {step_name} in round {data_manager.round_number}"
    )


def load_state(data_manager, starting_step):
    """Load state from JSON file when skipping steps"""
    state_file = Path(__file__).parent / "e2e_state.json"

    if not state_file.exists():
        raise Exception(
            f"Cannot start from step {starting_step}: State file {state_file} does not exist"
        )

    with open(state_file, "r") as f:
        state = json.load(f)

    # Load top-level data
    if "issue_uuid" in state:
        data_manager.issue_uuid = state["issue_uuid"]

    # Load all rounds data
    data_manager.rounds = state.get("rounds", {})

    # Get current round data
    round_key = str(data_manager.round_number)
    if round_key not in data_manager.rounds:
        data_manager.clear_round_data()
        return

    # Load current round data
    round_data = data_manager.rounds[round_key]
    data_manager.last_completed_step = round_data.get("last_completed_step")
    data_manager.ipfs_cid = round_data.get("ipfs_cid")
    data_manager.submission_data = round_data.get("submission_data", {})

    print(f"\nLoaded state from {state_file} for round {data_manager.round_number}")
    print(f"Starting from step {starting_step} with:")
    if data_manager.issue_uuid:
        print(f"Issue UUID: {data_manager.issue_uuid}")
    print(f"Round number: {data_manager.round_number}")
    if data_manager.last_completed_step:
        print(f"Last completed step: {data_manager.last_completed_step}")
        if data_manager.ipfs_cid:
            print(f"IPFS CID: {data_manager.ipfs_cid}")


def reset_mongodb(data_dir: Path = None, task_id: str = None):
    """Reset the MongoDB database by clearing collections and importing fresh test data"""
    print("\nResetting MongoDB database...")

    # Get data directory path - use provided path or default to tests/data
    if data_dir is None:
        data_dir = os.getenv("DATA_DIR")
    print(f"Using data directory: {data_dir}")

    # Check if files exist
    spec_path = data_dir / "spec.json"

    if not spec_path.exists():
        print(f"Error: spec.json not found at {spec_path}")
        return

    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    print(f"Connecting to MongoDB at: {mongodb_uri}")

    client = MongoClient(mongodb_uri)
    db = client["builder247"]

    try:
        # Clear collections
        print("\nClearing collections...")
        db.specs.delete_many({})
        db.systemprompts.delete_many({})
        db.audits.delete_many({})

        # Read and import specs
        print(f"\nReading specs from {spec_path}")
        with open(spec_path, "r") as f:
            specs_data = json.load(f)
            # Convert to array if it's a single object
            if not isinstance(specs_data, list):
                specs_data = [specs_data]

            # Add task_id to each spec if provided
            if task_id:
                for spec in specs_data:
                    spec["taskId"] = task_id

            # Insert specs
            if specs_data:
                print(f"Inserting {len(specs_data)} specs...")
                db.specs.insert_many(specs_data)
            else:
                print("No specs to insert")

        print("\nMongoDB reset complete!")

    except Exception as e:
        print(f"Error resetting MongoDB: {e}")
    finally:
        client.close()


def check_and_populate_db(data_dir: Path = None, task_id: str = None):
    """Check if MongoDB is populated and reset if needed"""
    mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongodb_uri)
    db = client["builder247"]

    try:
        # Check if we have any specs
        specs_count = db.specs.count_documents({})
        prompts_count = db.systemprompts.count_documents({})

        print(f"\nFound {specs_count} specs and {prompts_count} prompts in MongoDB")

        # If either collection is empty, reset the database
        if specs_count == 0 or prompts_count == 0:
            print("Database is empty or missing data, resetting...")
            reset_mongodb(data_dir, task_id)
        else:
            print("Database already populated, skipping reset")

    except Exception as e:
        print(f"Error checking MongoDB: {e}")
        print("Attempting to reset database...")
        reset_mongodb(data_dir, task_id)
    finally:
        client.close()


def run_test_sequence(
    test_setup,
    task_id: str = "",
    data_dir: Path = None,
    max_rounds: int = None,
):
    """Run the test sequence for the planner task"""
    # Initialize test data manager
    data_manager = DataManager(task_id=task_id, round_number=0)

    # Reset databases and check MongoDB
    reset_databases()
    check_and_populate_db(data_dir, task_id)

    # Start test sequence
    round_number = 0
    while True:
        if max_rounds is not None and round_number >= max_rounds:
            print(f"\nReached maximum rounds ({max_rounds}), stopping test sequence")
            break

        print(f"\n{'='*40} ROUND {round_number} {'='*40}")
        data_manager.round_number = round_number

        # Step 1: Worker fetches task
        log_step("1", "Worker fetches task")
        worker_task_payload = data_manager.prepare_worker_task("worker1", round_number)
        log_request("POST", "/api/planner/fetch-planner-todo", worker_task_payload)

        worker_task_response = test_setup.fetch_planner_todo(worker_task_payload)
        log_response(worker_task_response)

        if worker_task_response.status_code != 200:
            print("\nNo more work to do, test sequence complete!")
            break

        worker_task_data = worker_task_response.json()
        data_manager.issue_uuid = worker_task_data.get("data", {}).get("uuid")
        save_state(data_manager, "worker_task")

        # Step 2: Worker submits task result
        log_step("2", "Worker submits task result")
        # The actual task execution happens in the worker's pod
        # We just need to wait for the submission

        # Step 3: Worker audits task
        log_step("3", "Worker audits task")
        worker_audit_payload = data_manager.prepare_worker_audit(
            "worker2",
            data_manager.ipfs_cid,
            round_number,
            data_manager.submission_data,
        )
        log_request("POST", "/api/planner/audit", worker_audit_payload)

        worker_audit_response = test_setup.audit_planner(worker_audit_payload)
        log_response(worker_audit_response)
        save_state(data_manager, "worker_audit")

        # Increment round number
        round_number += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the test sequence for the builder task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The script will automatically determine where to resume from based on the saved state.
If no state exists, or if --reset is used, it will start from the beginning.
The current round is determined from the state file.

Example usage:
  # Run or resume the sequence
  python -m tests.e2e

  # Reset databases and start fresh
  python -m tests.e2e --reset

  # Run with specific task ID
  python -m tests.e2e --task-id 123abc

  # Run with custom data directory
  python -m tests.e2e --data-dir /path/to/data

  # Run with maximum number of rounds
  python -m tests.e2e --max-rounds 5
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
        "--max-rounds",
        type=int,
        help="Maximum number of rounds to run (overrides automatic calculation)",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else Path(os.getenv("DATA_DIR"))

    # Get task ID from environment if not provided
    task_id = args.task_id or os.getenv("TASK_ID")
    if not task_id:
        raise ValueError("No task ID provided and TASK_ID environment variable not set")

    # If reset is requested, do it before anything else
    if args.reset:
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

    print(f"Using task ID: {task_id}")

    # Initialize data manager with just task_id
    data_manager = DataManager(task_id=task_id)

    # Use TestSetup as a context manager to ensure servers are started and stopped properly
    with TestSetup() as test_setup:
        run_test_sequence(test_setup, task_id, data_dir, args.max_rounds)
