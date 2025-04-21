"""Stage for executing worker tasks."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker):
    """Prepare data for worker task"""
    # Create fetch-todo payload for stakingSignature and publicSignature
    fetch_todo_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
        "action": "fetch-todo",
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    # Create add-pr payload for addPRSignature
    add_pr_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
        "action": "add-todo-pr",
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    return {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
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

    if result.get("success") and "pr_url" in result:
        runner.state.setdefault("pr_urls", {})[worker.name] = result["pr_url"]

    return result
