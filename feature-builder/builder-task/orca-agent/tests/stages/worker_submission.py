"""Stage for handling worker submissions."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker):
    """Prepare data for worker submission"""
    if worker.name not in runner.state.get("pr_urls", {}):
        raise ValueError(f"No PR URL found for {worker.name}")

    # Get submission data from worker
    url = f"{worker.url}/submission/{runner.config.task_id}/{runner.current_round}"
    response = requests.get(url)
    response.raise_for_status()
    submission_data = response.json()

    # Create signature for the submission
    submitter_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
        "action": "audit",
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
        "prUrl": submission_data.get("prUrl"),
    }

    return {
        **submission_data,
        "signature": create_signature(worker.staking_signing_key, submitter_payload),
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }


def execute(runner, worker, data):
    """Store worker submission data"""
    return data
