"""Stage for executing worker tasks."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker):
    """Prepare data for worker task"""
    # Create fetch-todo payload for stakingSignature and publicSignature
    fetch_todo_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "action": "fetch-todo",
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    # Create add-pr payload for addPRSignature
    add_pr_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "action": "add-todo-pr",
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    return {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
        "stakingSignature": create_signature(
            worker.staking_signing_key, fetch_todo_payload
        ),
        "publicSignature": create_signature(
            worker.public_signing_key, fetch_todo_payload
        ),
        "addPRSignature": create_signature(worker.staking_signing_key, add_pr_payload),
    }


def execute(runner, worker, data):
    """Execute worker task step"""
    url = f"{worker.url}/worker-task/{data['roundNumber']}"
    response = requests.post(url, json=data)
    result = response.json()

    # Handle 409 gracefully - no eligible todos is an expected case
    if response.status_code in [401, 409]:
        print(
            f"✓ {result.get('message', 'No eligible todos')} for {worker.name} - continuing"
        )
        return {"success": True, "message": result.get("message")}

    if result.get("success") and "pr_url" in result:
        round_key = str(runner.current_round)
        round_state = runner.state["rounds"].setdefault(round_key, {})

        # Initialize pr_urls if not exists
        if "pr_urls" not in round_state:
            round_state["pr_urls"] = {}
        round_state["pr_urls"][worker.name] = result["pr_url"]

        # Initialize submission_data if not exists
        if "submission_data" not in round_state:
            round_state["submission_data"] = {}

        # Store submission data
        round_state["submission_data"][worker.name] = {
            "githubUsername": worker.env.get("GITHUB_USERNAME"),
            "nodeType": "worker",
            "prUrl": result["pr_url"],
            "repoName": result.get("repoName"),
            "repoOwner": result.get("repoOwner"),
            "roundNumber": runner.current_round,
            "taskId": runner.config.task_id,
            "uuid": result.get("uuid"),  # Should be provided by the worker
            "stakingKey": worker.staking_public_key,
            "pubKey": worker.public_key,
        }

    return result
