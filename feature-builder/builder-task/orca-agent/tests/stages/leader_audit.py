"""Stage for leader audits."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker):
    """Prepare data for leader audit"""
    round_state = runner.state["rounds"].get(str(runner.current_round), {})
    pr_urls = round_state.get("pr_urls", {})
    if "leader" not in pr_urls:
        # Return None to indicate this step should be skipped
        print("✓ No PR URL found for leader, skipping leader audit - continuing")
        return None

    # Get submission data from state
    submission_data = round_state.get("submission_data", {}).get("leader")
    if not submission_data:
        # Return None to indicate this step should be skipped
        print(
            "✓ No submission data found for leader, skipping leader audit - continuing"
        )
        return None

    # Create auditor payload which is used to generate the signature
    auditor_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "prUrl": pr_urls["leader"],
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    # Structure the payload according to what the server expects
    return {
        "submission": {
            "taskId": runner.config.task_id,
            "roundNumber": runner.current_round,
            "prUrl": pr_urls["leader"],
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
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
        "stakingSignature": create_signature(
            worker.staking_signing_key, auditor_payload
        ),
        "publicSignature": create_signature(worker.public_signing_key, auditor_payload),
        "prUrl": pr_urls["leader"],
        "repoOwner": submission_data.get("repoOwner"),
        "repoName": submission_data.get("repoName"),
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
    }


def execute(runner, worker, data):
    """Execute leader audit step"""
    # If prepare returned None, skip this step
    if data is None:
        return {
            "success": True,
            "message": "Skipped due to missing PR URL or submission data",
        }

    url = f"{worker.url}/leader-audit/{runner.current_round}"
    response = requests.post(url, json=data)
    result = response.json()

    return result
