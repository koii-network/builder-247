"""Stage for leader audits."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker):
    """Prepare data for leader audit"""
    if "leader" not in runner.state.get("pr_urls", {}):
        raise ValueError("No PR URL found for leader")

    # Get submission data from leader
    url = f"{worker.url}/submission/{runner.config.task_id}/{runner.round_number}"
    response = requests.get(url)
    response.raise_for_status()
    submission_data = response.json()

    # Create auditor payload which is used to generate the signature
    auditor_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
        "prUrl": runner.state["pr_urls"]["leader"],
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    # Structure the payload according to what the server expects
    return {
        "submission": {
            "taskId": runner.config.task_id,
            "roundNumber": runner.round_number,
            "prUrl": runner.state["pr_urls"]["leader"],
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
        "prUrl": runner.state["pr_urls"]["leader"],
        "repoOwner": submission_data.get("repoOwner"),
        "repoName": submission_data.get("repoName"),
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
    }


def execute(runner, worker, data):
    """Execute leader audit step"""
    url = f"{worker.url}/leader-audit/{data['roundNumber']}"
    response = requests.post(url, json=data)
    return response.json()
