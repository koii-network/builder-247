"""Stage for leader tasks."""

import requests
from prometheus_test.utils import create_signature


def prepare(runner, worker):
    """Prepare data for leader task"""
    # Create fetch-issue payload for stakingSignature and publicSignature
    fetch_issue_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "action": "fetch-issue",
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    # Create add-pr payload for addPRSignature
    add_pr_payload = {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "action": "add-issue-pr",
        "githubUsername": worker.env.get("GITHUB_USERNAME"),
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
    }

    return {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "stakingKey": worker.staking_public_key,
        "pubKey": worker.public_key,
        "stakingSignature": create_signature(
            worker.staking_signing_key, fetch_issue_payload
        ),
        "publicSignature": create_signature(
            worker.public_signing_key, fetch_issue_payload
        ),
        "addPRSignature": create_signature(worker.staking_signing_key, add_pr_payload),
    }


def execute(runner, worker, data):
    """Execute leader task step"""
    url = f"{worker.url}/leader-task/{data['roundNumber']}"
    response = requests.post(url, json=data)
    result = response.json()

    # Handle 409 gracefully - no eligible issues is an expected case
    if response.status_code == 409:
        print(f"✓ {result.get('message', 'No eligible issues')} - continuing")
        return {"success": True, "message": result.get("message")}

    if result.get("success") and "pr_url" in result:
        round_key = str(runner.current_round)
        round_state = runner.state["rounds"].setdefault(round_key, {})

        # Initialize pr_urls if not exists
        if "pr_urls" not in round_state:
            round_state["pr_urls"] = {}
        round_state["pr_urls"]["leader"] = result["pr_url"]

        # Initialize submission_data if not exists
        if "submission_data" not in round_state:
            round_state["submission_data"] = {}

        # Store submission data
        round_state["submission_data"]["leader"] = {
            "githubUsername": worker.env.get("GITHUB_USERNAME"),
            "nodeType": "leader",
            "prUrl": result["pr_url"],
            "repoName": result.get("repoName"),
            "repoOwner": result.get("repoOwner"),
            "roundNumber": runner.current_round,
            "taskId": runner.config.task_id,
            "uuid": runner.state.get("issue_uuid"),  # Leader uses the issue UUID
            "stakingKey": worker.staking_public_key,
            "pubKey": worker.public_key,
        }

    return result
