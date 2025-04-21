"""Stage for leader tasks."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner):
    """Prepare data for leader task"""
    worker = runner.get_worker("leader")
    payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }
    return {
        **payload,
        "stakingSignature": create_signature(worker.staking_signing_key, payload),
    }


def execute(runner, data):
    """Execute leader task step"""
    worker = runner.get_worker("leader")
    url = f"{worker.url}/leader-task/{data['roundNumber']}"
    response = requests.post(url, json=data)
    result = response.json()

    if result.get("success") and "pr_url" in result:
        runner.state.setdefault("pr_urls", {})["leader"] = result["pr_url"]

    return result
