import os
from pathlib import Path
from prometheus_test import TaskTestRunner, TestStep, ServerConfig
from pymongo import MongoClient
import uuid
import json
import requests


def reset_databases(builder_path: Path):
    """Delete all database files before starting the test sequence"""
    for role in ["leader", "worker1", "worker2"]:
        db_path = builder_path / f"database_{role}.db"
        if db_path.exists():
            print(f"Deleting database file: {db_path}")
            os.remove(db_path)


def reset_mongodb(data_dir: Path, task_id: str = None):
    """Reset MongoDB database and import test data"""
    print("\nResetting MongoDB database...")

    # Check if files exist
    issues_path = data_dir / "issues.json"
    todos_path = data_dir / "todos.json"
    prompts_path = data_dir / "prompts.json"

    for path in [issues_path, todos_path, prompts_path]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    print(f"Connecting to MongoDB at: {mongodb_uri}")

    client = MongoClient(mongodb_uri)
    db = client["builder247"]

    # Clear collections
    print("\nClearing collections...")
    for collection in ["issues", "todos", "systemprompts", "audits"]:
        db[collection].delete_many({})

    # Import issues
    with open(issues_path) as f:
        issues_data = json.load(f)
        if not isinstance(issues_data, list):
            issues_data = [issues_data]

        if task_id:
            for issue in issues_data:
                issue["taskId"] = task_id

        # Add UUIDs to issues
        for issue in issues_data:
            new_uuid = str(uuid.uuid4())
            issue["issueUuid"] = new_uuid
            issue["uuid"] = new_uuid

        db.issues.insert_many(issues_data)

    # Import todos
    with open(todos_path) as f:
        todos_data = json.load(f)
        if not isinstance(todos_data, list):
            todos_data = [todos_data]

        if task_id:
            for todo in todos_data:
                todo["taskId"] = task_id

        # Create UUID mapping
        todo_mapping = {}
        for todo in todos_data:
            todo["uuid"] = str(uuid.uuid4())
            todo_mapping[todo["title"]] = todo["uuid"]

        # Update dependencies
        for todo in todos_data:
            if "dependencyTasks" in todo:
                todo["dependencyTasks"] = [
                    todo_mapping.get(title, title) for title in todo["dependencyTasks"]
                ]

        db.todos.insert_many(todos_data)


def prepare_create_repo(context):
    """Prepare data for creating a repository"""
    return {
        "taskId": context.task_id,
        "roundNumber": context.round_number,
        "action": "create-repo",
    }


def execute_create_repo(context, data):
    """Execute repository creation step"""
    server = context.get_server("leader")
    url = f"{server.url}/create-aggregator-repo/{data['taskId']}"
    response = requests.post(url, json=data)
    result = response.json()

    if result.get("success"):
        context.current_state["fork_url"] = result["data"]["fork_url"]
        context.current_state["issue_uuid"] = result["data"]["issue_uuid"]

    return result


def prepare_worker_task(context):
    """Prepare data for worker task"""
    return {
        "taskId": context.task_id,
        "roundNumber": context.round_number,
        "stakingKey": "dummy_staking_key",  # Replace with real key
        "pubKey": "dummy_pub_key",  # Replace with real key
        "stakingSignature": "dummy_signature",  # Replace with real signature
        "publicSignature": "dummy_signature",  # Replace with real signature
        "addPRSignature": "dummy_signature",  # Replace with real signature
    }


def execute_worker_task(context, data):
    """Execute worker task step"""
    server = context.get_server("worker1")
    url = f"{server.url}/worker-task/{data['roundNumber']}"
    response = requests.post(url, json=data)
    result = response.json()

    if result.get("success") and "pr_url" in result:
        context.current_state.setdefault("pr_urls", {})["worker1"] = result["pr_url"]

    return result


def prepare_worker_audit(context):
    """Prepare data for worker audit"""
    pr_urls = context.current_state.get("pr_urls", {})
    if not pr_urls.get("worker1"):
        raise ValueError("No PR URL found for worker1")

    return {
        "taskId": context.task_id,
        "roundNumber": context.round_number,
        "prUrl": pr_urls["worker1"],
        "stakingKey": "dummy_staking_key",  # Replace with real key
        "pubKey": "dummy_pub_key",  # Replace with real key
        "stakingSignature": "dummy_signature",  # Replace with real signature
        "publicSignature": "dummy_signature",  # Replace with real signature
    }


def execute_worker_audit(context, data):
    """Execute worker audit step"""
    server = context.get_server("worker2")
    url = f"{server.url}/worker-audit/{data['roundNumber']}"
    response = requests.post(url, json=data)
    return response.json()


def main():
    # Setup paths
    builder_path = (
        Path(__file__).parent.parent / "feature-builder" / "builder-task" / "orca-agent"
    )
    data_dir = builder_path / "tests" / "data"

    # Reset state
    reset_databases(builder_path)
    reset_mongodb(data_dir, task_id="test-task-123")

    # Configure servers
    server_configs = [
        ServerConfig(
            name="leader",
            port=5000,
            env_vars={
                "GITHUB_TOKEN": os.getenv("LEADER_GITHUB_TOKEN"),
                "GITHUB_USERNAME": os.getenv("LEADER_GITHUB_USERNAME"),
                "PORT": "5000",
            },
            startup_script=builder_path / "main.py",
            database_path=builder_path / "database_leader.db",
        ),
        ServerConfig(
            name="worker1",
            port=5001,
            env_vars={
                "GITHUB_TOKEN": os.getenv("WORKER1_GITHUB_TOKEN"),
                "GITHUB_USERNAME": os.getenv("WORKER1_GITHUB_USERNAME"),
                "PORT": "5001",
            },
            startup_script=builder_path / "main.py",
            database_path=builder_path / "database_worker1.db",
        ),
        ServerConfig(
            name="worker2",
            port=5002,
            env_vars={
                "GITHUB_TOKEN": os.getenv("WORKER2_GITHUB_TOKEN"),
                "GITHUB_USERNAME": os.getenv("WORKER2_GITHUB_USERNAME"),
                "PORT": "5002",
            },
            startup_script=builder_path / "main.py",
            database_path=builder_path / "database_worker2.db",
        ),
    ]

    # Define test steps
    steps = [
        TestStep(
            name="create_repo",
            description="Create aggregator repository",
            prepare_data=prepare_create_repo,
            execute_step=execute_create_repo,
        ),
        TestStep(
            name="worker_task",
            description="Execute worker task",
            prepare_data=prepare_worker_task,
            execute_step=execute_worker_task,
        ),
        TestStep(
            name="worker_audit",
            description="Execute worker audit",
            prepare_data=prepare_worker_audit,
            execute_step=execute_worker_audit,
        ),
    ]

    # Create test runner
    runner = TaskTestRunner(
        task_id="test-task-123",
        data_dir=data_dir,
        server_configs=server_configs,
        steps=steps,
        max_rounds=3,
    )

    # Run test sequence
    runner.run(reset_state=True)


if __name__ == "__main__":
    main()
