"""Stage for updating audit results."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, role: str):
    """Prepare data for updating audit results"""
    worker = runner.get_worker("leader" if role == "leader" else "worker1")
    payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
        "role": role,
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }
    return {
        **payload,
        "stakingSignature": create_signature(worker.staking_signing_key, payload),
    }


def execute(runner, data):
    """Execute audit results update"""
    worker = runner.get_worker("leader" if data["role"] == "leader" else "worker1")
    url = f"{worker.url}/audit-results/{data['roundNumber']}"
    response = requests.post(url, json=data)
    return response.json()
