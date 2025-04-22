"""Stage for updating audit results."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker, role: str):
    """Prepare data for updating audit results"""
    # Create payload with all required fields
    payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "role": role,
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    return {
        **payload,
        "stakingSignature": create_signature(worker.staking_signing_key, payload),
    }


def execute(runner, worker, data):
    """Execute audit results update"""
    url = f"{worker.url}/update-audit-result/{runner.config.task_id}/{data['roundNumber']}"

    # Structure the payload according to what the server expects
    payload = {
        "taskId": runner.config.task_id,
        "round": data["roundNumber"],
        "auditType": data["role"],
    }

    response = requests.post(url, json=payload)
    result = response.json()

    if not result.get("success", False):
        raise Exception(
            f"Update audit result failed: {result.get('message', 'Unknown error')}"
        )

    return result
