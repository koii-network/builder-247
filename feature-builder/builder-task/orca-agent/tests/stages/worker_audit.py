"""Stage for worker audits."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker, target_name):
    """Prepare data for worker audit"""
    pr_urls = runner.state.get("pr_urls", {})
    if target_name not in pr_urls:
        raise ValueError(f"No PR URL found for {target_name}")

    return {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
        "prUrl": pr_urls[target_name],
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
        "stakingSignature": create_signature(
            worker.staking_signing_key,
            {
                "taskId": runner.config.task_id,
                "roundNumber": runner.round_number,
                "stakingKey": worker.staking_public_key,
                "pubKey": worker.public_key,
            },
        ),
        "publicSignature": create_signature(
            worker.public_signing_key,
            {
                "taskId": runner.config.task_id,
                "roundNumber": runner.round_number,
                "stakingKey": worker.staking_public_key,
                "pubKey": worker.public_key,
            },
        ),
    }


def execute(runner, worker, data):
    """Execute worker audit step"""
    url = f"{worker.url}/worker-audit/{data['roundNumber']}"
    response = requests.post(url, json=data)
    return response.json()
