"""Stage for worker audits."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker, target_name):
    """Prepare data for worker audit"""
    pr_urls = runner.state.get("pr_urls", {})
    if target_name not in pr_urls:
        raise ValueError(f"No PR URL found for {target_name}")

    # Create auditor payload which is used to generate the signature
    auditor_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
        "prUrl": pr_urls[target_name],
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    # Get submission data from target worker
    target_worker = runner.get_worker(target_name)
    url = (
        f"{target_worker.url}/submission/{runner.config.task_id}/{runner.round_number}"
    )
    response = requests.get(url)
    response.raise_for_status()
    submission_data = response.json()

    # Structure the payload according to what the server expects
    return {
        "submission": {
            "taskId": runner.config.task_id,
            "roundNumber": runner.round_number,
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
    url = f"{worker.url}/worker-audit/{data['roundNumber']}"
    response = requests.post(url, json=data)
    return response.json()
