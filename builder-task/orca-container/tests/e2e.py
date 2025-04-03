import requests
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


def reset_mongodb():
    """Reset the MongoDB database by clearing collections and importing fresh test data"""
    print("\nResetting MongoDB database...")

    # Get data directory path
    data_dir = Path(os.getenv("DATA_DIR", os.path.dirname(__file__)))
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

        # Verify collections are empty
        print("\nVerifying collections are empty...")
        issues_count = db.issues.count_documents({})
        todos_count = db.todos.count_documents({})
        prompts_count = db.systemprompts.count_documents({})
        print(f"Current issues count after delete: {issues_count}")
        print(f"Current todos count after delete: {todos_count}")
        print(f"Current prompts count after delete: {prompts_count}")

        # Read and import issues
        print(f"\nReading issues from {issues_path}")
        with open(issues_path, "r") as f:
            issues_data = json.load(f)
            print(f"Issues data to import: {json.dumps(issues_data, indent=2)}")
            result = db.issues.insert_one(issues_data)
            print(f"Imported issue with ID: {result.inserted_id}")

        # Read and import todos
        print(f"\nReading todos from {todos_path}")
        with open(todos_path, "r") as f:
            todos_data = json.load(f)
            result = db.todos.insert_many(todos_data)
            print(f"Imported {len(result.inserted_ids)} todos")

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
        print(f"Final issues count: {issues_count}")
        print(f"Final todos count: {todos_count}")
        print(f"Final prompts count: {prompts_count}")

        print("\nMongoDB database reset completed successfully")
    except Exception as e:
        print(f"Error resetting MongoDB database: {e}")
        raise
    finally:
        client.close()


def run_test_sequence(
    start_step: int = 1,
    stop_step: int = 5,
    reset_db: bool = False,
    reset_mongo: bool = False,
):
    """Run the test sequence from start_step to stop_step (inclusive)"""
    if reset_db:
        reset_databases()
    if reset_mongo:
        reset_mongodb()

    with TestSetup() as setup:
        data_manager = DataManager()
        pr_urls = {}  # Store PR URLs for later use

        try:
            # 1. Create aggregator repo
            if start_step <= 1 <= stop_step:
                log_step(1, "Creating aggregator repo")
                setup.switch_role("leader")
                payload = data_manager.prepare_create_aggregator_repo()

                url = f"{setup.current_server.url}/create-aggregator-repo/{data_manager.task_id}"
                log_request("POST", url, payload)
                response = requests.post(url, json=payload)
                log_response(response)

                result = response.json()
                if not result.get("success"):
                    raise Exception(
                        f"Failed to create aggregator repo: {result.get('message')}"
                    )
                print("\n" + "=" * 40)
                print("✓ AGGREGATOR REPO CREATED SUCCESSFULLY")
                print("=" * 40)
                fork_url = result.get("data", {}).get("fork_url")
                branch_name = result.get("data", {}).get("branch_name")
                if not fork_url or not branch_name:
                    raise Exception("Missing fork_url or branch_name in response")
                print(f"✓ Fork URL: {fork_url}")
                print(f"✓ Branch name: {branch_name}")

                # Store the fork URL and branch name for use in subsequent steps
                data_manager.fork_url = fork_url
                data_manager.branch_name = branch_name

                # Extract repository name from fork URL
                repo_parts = fork_url.strip("/").split("/")
                if len(repo_parts) >= 2:
                    aggregator_owner = repo_parts[-2]
                    repo_name = repo_parts[-1]
                    print(
                        f"✓ Using repository information from fork: {aggregator_owner}/{repo_name}"
                    )
                else:
                    print(
                        f"⚠️ Could not extract repository information from fork URL: {fork_url}"
                    )

                # Now call the add-aggregator-info endpoint to update the middle server
                print("\nCalling add-aggregator-info endpoint...")

                # Prepare the payload for add-aggregator-info
                aggregator_payload = data_manager.prepare_aggregator_info("leader", 1)

                url = f"{setup.current_server.url}/add-aggregator-info/{data_manager.task_id}"
                log_request("POST", url, aggregator_payload)
                response = requests.post(url, json=aggregator_payload)
                log_response(response)

                result = response.json()
                if not result.get("success"):
                    raise Exception(
                        f"Failed to add aggregator info: {result.get('message')}"
                    )
                print("✓ Aggregator info updated successfully")

            # 2. Worker tasks (Worker 1 and Worker 2)
            if start_step <= 2 <= stop_step:
                log_step(2, "Running Worker tasks")

                # Worker 1 task
                setup.switch_role("worker1")
                payload = data_manager.prepare_worker_task("worker1", 1)

                url = f"{setup.current_server.url}/worker-task/1"
                log_request("POST", url, payload)
                response = requests.post(url, json=payload)
                log_response(response)

                result = response.json()
                if not result.get("success"):
                    raise Exception(f"Worker 1 task failed: {result.get('message')}")
                pr_urls["worker1"] = result.get("pr_url")
                print(f"✓ Worker 1 PR created: {pr_urls['worker1']}")

                # Worker 2 task
                setup.switch_role("worker2")
                payload = data_manager.prepare_worker_task("worker2", 1)

                url = f"{setup.current_server.url}/worker-task/1"
                log_request("POST", url, payload)
                response = requests.post(url, json=payload)
                log_response(response)

                result = response.json()
                if not result.get("success"):
                    raise Exception(f"Worker 2 task failed: {result.get('message')}")
                pr_urls["worker2"] = result.get("pr_url")
                print(f"✓ Worker 2 PR created: {pr_urls['worker2']}")

            # 3. Cross audits
            if start_step <= 3 <= stop_step:
                log_step(3, "Running cross audits")
                print("\nWorker 2 auditing Worker 1's PR...")
                setup.switch_role("worker2")
                payload = data_manager.prepare_worker_audit(
                    "worker2", pr_urls["worker1"], 1
                )

                url = f"{setup.current_server.url}/worker-audit/1"
                log_request("POST", url, payload)
                response = requests.post(url, json=payload)
                log_response(response)

                result = response.json()
                if not result.get("success"):
                    raise Exception(f"Worker 2 audit failed: {result.get('message')}")
                print("✓ Worker 2 audit complete")

                print("\nWorker 1 auditing Worker 2's PR...")
                setup.switch_role("worker1")
                payload = data_manager.prepare_worker_audit(
                    "worker1", pr_urls["worker2"], 1
                )

                url = f"{setup.current_server.url}/worker-audit/1"
                log_request("POST", url, payload)
                response = requests.post(url, json=payload)
                log_response(response)

                result = response.json()
                if not result.get("success"):
                    raise Exception(f"Worker 1 audit failed: {result.get('message')}")
                print("✓ Worker 1 audit complete")

            # 4. Leader task
            if start_step <= 4 <= stop_step:
                log_step(4, "Running leader task")
                setup.switch_role("leader")
                payload = data_manager.prepare_leader_task(
                    "leader", 4, [pr_urls["worker1"], pr_urls["worker2"]]
                )

                url = f"{setup.current_server.url}/leader-task/4"
                log_request("POST", url, payload)
                response = requests.post(url, json=payload)
                log_response(response)

                result = response.json()
                if not result.get("success"):
                    raise Exception(f"Leader task failed: {result.get('message')}")
                pr_urls["leader"] = result.get("pr_url")
                print(f"✓ Leader PR created: {pr_urls['leader']}")

            # 5. Leader audits
            if start_step <= 5 <= stop_step:
                log_step(5, "Running leader audits")
                print("\nFirst leader audit...")
                setup.switch_role("worker1")
                payload = data_manager.prepare_worker_audit(
                    "worker1", pr_urls["leader"], 4
                )

                url = f"{setup.current_server.url}/leader-audit/4"
                log_request("POST", url, payload)
                response = requests.post(url, json=payload)
                log_response(response)

                result = response.json()
                if not result.get("success"):
                    raise Exception(
                        f"First leader audit failed: {result.get('message')}"
                    )
                print("✓ First leader audit complete")

            print("\n" + "=" * 80)
            print("TEST SEQUENCE COMPLETED SUCCESSFULLY")
            print("=" * 80)

        except Exception as e:
            print("\n" + "!" * 80)
            print(f"TEST SEQUENCE FAILED: {str(e)}")
            print("!" * 80)
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the test sequence for the builder task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available steps:
  1. Create aggregator repo
  2. Worker tasks (Worker 1 and Worker 2)
  3. Cross audits (Worker 2 audits Worker 1, then Worker 1 audits Worker 2)
  4. Leader task
  5. Leader audits

Example usage:
  # Run the full sequence
  python -m tests.e2e

  # Run only worker tasks and cross audits
  python -m tests.e2e --start 2 --stop 3

  # Reset databases and run specific steps
  python -m tests.e2e --start 2 --stop 4 --reset-db --reset-mongo
""",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Start step number (1-5)",
    )
    parser.add_argument(
        "--stop",
        type=int,
        default=5,
        help="Stop step number (1-5)",
    )
    parser.add_argument(
        "--reset-db", action="store_true", help="Reset SQLite databases before running"
    )
    parser.add_argument(
        "--reset-mongo",
        action="store_true",
        help="Reset MongoDB database before running",
    )
    args = parser.parse_args()

    # Validate step numbers
    if not (1 <= args.start <= 5 and 1 <= args.stop <= 5):
        print("Error: Step numbers must be between 1 and 5")
        exit(1)
    if args.start > args.stop:
        print("Error: Start step cannot be greater than stop step")
        exit(1)

    run_test_sequence(args.start, args.stop, args.reset_db, args.reset_mongo)
