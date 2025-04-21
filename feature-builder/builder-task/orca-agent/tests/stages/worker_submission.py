"""Stage for handling worker submissions."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker):
    """Prepare data for worker submission"""
    # Get the current round's state
    round_state = runner.state.get("rounds", {}).get(str(runner.current_round), {})
    pr_urls = round_state.get("pr_urls", {})

    if worker.name not in pr_urls:
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
    # Store submission data in state
    round_key = str(runner.current_round)
    round_state = runner.state["rounds"].setdefault(round_key, {})

    # Initialize submission_data if not exists
    if "submission_data" not in round_state:
        round_state["submission_data"] = {}

    # Store or update submission data
    round_state["submission_data"][worker.name] = data

    # Return success result
    return {"success": True, "data": data}
