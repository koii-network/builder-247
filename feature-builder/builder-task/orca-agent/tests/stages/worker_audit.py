"""Stage for worker audits."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker, target_name):
    """Prepare data for worker audit"""
    round_state = runner.state["rounds"].get(str(runner.current_round), {})
    pr_urls = round_state.get("pr_urls", {})

    if target_name not in pr_urls:
        # Return None to indicate this step should be skipped
        print(
            f"✓ No PR URL found for {target_name}, skipping {worker.name} audit - continuing"
        )
        return None

    # Get submission data from state
    submission_data = round_state.get("submission_data", {}).get(target_name)
    if not submission_data:
        # Return None to indicate this step should be skipped
        print(
            f"✓ No submission data found for {target_name}, skipping {worker.name} audit - continuing"
        )
        return None

    # Create auditor payload which is used to generate the signature
    auditor_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "prUrl": pr_urls[target_name],
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    # Structure the payload according to what the server expects
    return {
        "submission": {
            "taskId": runner.config.task_id,
            "roundNumber": runner.current_round,
            "prUrl": pr_urls[target_name],
            "githubUsername": submission_data.get("githubUsername"),
            "repoOwner": submission_data.get("repoOwner"),
            "repoName": submission_data.get("repoName"),
            "stakingKey": submission_data.get("stakingKey"),
            "pubKey": submission_data.get("pubKey"),
            "uuid": submission_data.get("uuid"),
            "nodeType": submission_data.get("nodeType"),
        },
        "submitterSignature": submission_data.get("signature"),
        "submitterStakingKey": submission_data.get("stakingKey"),
        "submitterPubKey": submission_data.get("pubKey"),
        "prUrl": pr_urls[target_name],
        "repoOwner": submission_data.get("repoOwner"),
        "repoName": submission_data.get("repoName"),
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
        "stakingSignature": create_signature(
            worker.staking_signing_key, auditor_payload
        ),
        "publicSignature": create_signature(worker.public_signing_key, auditor_payload),
    }


def execute(runner, worker, data):
    """Execute worker audit step"""
    # If prepare returned None, skip this step
    if data is None:
        return {
            "success": True,
            "message": "Skipped due to missing PR URL or submission data",
        }

    url = f"{worker.url}/worker-audit/{runner.current_round}"
    response = requests.post(url, json=data)
    result = response.json()

    return result
