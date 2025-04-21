"""Stage for executing worker tasks."""

import os
import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker_name="worker1"):
    """Prepare data for worker task"""
    worker = runner.get_worker(worker_name)

    # Prepare base payload for task signatures
    task_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    # Prepare PR submission payload
    pr_payload = {
        **task_payload,
        "action": "audit",
        "githubUsername": os.getenv(f"{worker_name.upper()}_GITHUB_USERNAME"),
    }

    # Create signatures using appropriate payloads
    return {
        **task_payload,
        "stakingSignature": create_signature(worker.staking_signing_key, task_payload),
        "publicSignature": create_signature(worker.public_signing_key, task_payload),
        "addPRSignature": create_signature(worker.staking_signing_key, pr_payload),
    }


def execute(runner, data, worker_name="worker1"):
    """Execute worker task step"""
    worker = runner.get_worker(worker_name)
    url = f"{worker.url}/worker-task/{data['roundNumber']}"
    response = requests.post(url, json=data)
    result = response.json()

    if result.get("success") and "pr_url" in result:
        runner.state.setdefault("pr_urls", {})[worker_name] = result["pr_url"]

    return result
