"""Stage for leader audits."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker):
    """Prepare data for leader audit"""
    if "leader" not in runner.state.get("pr_urls", {}):
        raise ValueError("No PR URL found for leader")

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


def execute(runner, worker, data):
    """Execute leader audit step"""
    url = f"{worker.url}/leader-audit/{data['roundNumber']}"
    response = requests.post(url, json=data)
    return response.json()
