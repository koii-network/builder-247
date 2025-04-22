"""Stage for recording the aggregator repository."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker):
    """Prepare data for recording aggregator info"""
    if "fork_url" not in runner.state or "issue_uuid" not in runner.state:
        raise ValueError("Fork URL or Issue UUID not found in state")

    # Create payload with all required fields
    payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "action": "create-repo",
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
        "issueUuid": runner.state["issue_uuid"],
        "aggregatorUrl": runner.state["fork_url"],
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    return {
        **payload,
        "signature": create_signature(worker.staking_signing_key, payload),
    }


def execute(runner, worker, data):
    """Execute recording of aggregator info"""
    url = f"{worker.url}/add-aggregator-info/{data['taskId']}"
    response = requests.post(url, json=data)
    return response.json()
