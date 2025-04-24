"""Test stage for auditing summary."""

import requests
from prometheus_test import Context


async def prepare(context: Context, target_name: str):
    """Prepare for auditing summary."""
    staking_key = context.env.get("WORKER_ID")
    target_submission = await context.storeGet(f"submission-{target_name}")

    return {
        "staking_key": staking_key,
        "round_number": context.round_number,
        "target_submission": target_submission,
        "target_name": target_name,
    }


async def execute(context: Context, prepare_data: dict):
    """Execute summary audit test."""
    staking_key = prepare_data["staking_key"]
    round_number = prepare_data["round_number"]
    target_submission = prepare_data["target_submission"]
    target_name = prepare_data["target_name"]

    # Mock response for audit
    response = requests.post(
        "http://localhost:5000/api/summarizer/audit",
        json={
            "taskId": context.config.task_id,
            "roundNumber": round_number,
            "stakingKey": staking_key,
            "submitterKey": target_name,
            "cid": target_submission.get("cid"),
            "prUrl": target_submission.get("pr_url"),
            "githubUsername": target_submission.get("github_username"),
        },
    )

    if response.status_code != 200:
        raise Exception(f"Failed to audit summary: {response.text}")

    result = response.json()
    if not result.get("success"):
        raise Exception("Failed to audit summary")

    # Store audit result
    await context.storeSet(f"audit-{staking_key}-{target_name}", result.get("data"))

    return True
