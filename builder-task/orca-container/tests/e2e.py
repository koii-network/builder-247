import requests
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
    print(f"PR URLs: {pr_urls}")


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
        # Also clear audits collection
        result = db.audits.delete_many({})
        print(f"Cleared {result.deleted_count} audits")

        # Verify collections are empty
        print("\nVerifying collections are empty...")
        issues_count = db.issues.count_documents({})
        todos_count = db.todos.count_documents({})
        prompts_count = db.systemprompts.count_documents({})
        audits_count = db.audits.count_documents({})
        print(f"Current issues count after delete: {issues_count}")
        print(f"Current todos count after delete: {todos_count}")
        print(f"Current prompts count after delete: {prompts_count}")
        print(f"Current audits count after delete: {audits_count}")

        # Generate a real UUID for the issue
        issue_uuid = str(uuid.uuid4())
        print(f"\nGenerated issue UUID: {issue_uuid}")

        # Read and import issues
        print(f"\nReading issues from {issues_path}")
        with open(issues_path, "r") as f:
            issues_data = json.load(f)
            # Replace the hardcoded UUID with the generated one
            issues_data["issueUuid"] = issue_uuid
            print(f"Issues data to import: {json.dumps(issues_data, indent=2)}")
            result = db.issues.insert_one(issues_data)
            print(f"Imported issue with ID: {result.inserted_id}")

        # Read and import todos
        print(f"\nReading todos from {todos_path}")
        with open(todos_path, "r") as f:
            todos_data = json.load(f)
            # Update each todo with a real UUID and link it to the issue
            for i, todo in enumerate(todos_data):
                todo["uuid"] = str(uuid.uuid4())
                todo["issueUuid"] = issue_uuid
                print(f"Generated todo UUID for todo {i+1}: {todo['uuid']}")

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


def run_test_sequence(
    start_step: int = 1,
    stop_step: int = 6,
    reset: bool = False,
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

        print(
            "Reset completed: SQLite databases, MongoDB, and state file have been reset"
        )

    with TestSetup() as setup:
        data_manager = DataManager()
        pr_urls = {}  # Store PR URLs for later use

        # If we're resetting or starting from step 1, get the issue UUID from MongoDB
        if reset or start_step == 1:
            mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/todos")
            client = MongoClient(mongodb_uri)
            db = client["todos"]

            try:
                # Get the issue from MongoDB
                issue = db.issues.find_one()
                if issue:
                    data_manager.issue_uuid = issue["issueUuid"]
                    print(f"Using issue UUID from MongoDB: {data_manager.issue_uuid}")
            except Exception as e:
                print(f"Error fetching issue from MongoDB: {e}")
            finally:
                client.close()

        # Load state if starting from a later step
        if start_step > 1:
            try:
                load_state(data_manager, pr_urls, start_step)
            except Exception as e:
                print(f"Error loading state: {e}")
                return

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
                issue_uuid = result.get("data", {}).get("issue_uuid")
                if not fork_url or not branch_name:
                    raise Exception("Missing fork_url or branch_name in response")
                print(f"✓ Fork URL: {fork_url}")
                print(f"✓ Branch name: {branch_name}")
                print(f"✓ Issue UUID: {issue_uuid}")

                # Store the fork URL and branch name for use in subsequent steps
                data_manager.fork_url = fork_url
                data_manager.branch_name = branch_name
                data_manager.issue_uuid = issue_uuid

                # Extract repository name from fork URL
                repo_parts = fork_url.strip("/").split("/")
                if len(repo_parts) >= 2:
                    aggregator_owner = repo_parts[-2]
                    repo_name = repo_parts[-1]
                    data_manager.repo_owner = aggregator_owner
                    data_manager.repo_name = repo_name
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

                # Save state after completing step 1
                save_state(data_manager, pr_urls, 1)

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

                # Save state after completing step 2
                save_state(data_manager, pr_urls, 2)

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

                # Save state after completing step 3
                save_state(data_manager, pr_urls, 3)

            # 4. Update audit results (separate step)
            if start_step <= 4 <= stop_step:
                log_step(4, "Updating audit results")
                setup.switch_role("leader")

                # Prepare update-audit-result payload
                update_payload = {
                    "taskId": data_manager.task_id,
                    "round": 1,  # Worker round is 1
                }

                url = f"{os.getenv('MIDDLE_SERVER_URL')}/api/update-audit-result"
                log_request("POST", url, update_payload)
                response = requests.post(url, json=update_payload)
                log_response(response)

                result = response.json()
                if not result.get("success", False):
                    print(
                        f"⚠️ Warning: Update audit result failed: {result.get('message', 'Unknown error')}"
                    )
                else:
                    print("✓ Audit results updated successfully")

                # Save state after completing step 4
                save_state(data_manager, pr_urls, 4)

            # 5. Leader task (renumbered from 4)
            if start_step <= 5 <= stop_step:
                log_step(5, "Running leader task")
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

                # Save state after completing step 5
                save_state(data_manager, pr_urls, 5)

            # 6. Leader audits (renumbered from 5)
            if start_step <= 6 <= stop_step:
                log_step(6, "Running leader audits")
                print("\nLeader audit...")
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
                    raise Exception(f"Leader audit failed: {result.get('message')}")
                print("✓ Leader audit complete")

                # Save state after completing step 6
                save_state(data_manager, pr_urls, 6)

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
    args = parser.parse_args()

    # Validate step numbers
    if not (1 <= args.start <= 6 and 1 <= args.stop <= 6):
        print("Error: Step numbers must be between 1 and 6")
        exit(1)
    if args.start > args.stop:
        print("Error: Start step cannot be greater than stop step")
        exit(1)

    run_test_sequence(args.start, args.stop, args.reset)
