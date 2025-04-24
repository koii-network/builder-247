"""Test stage for submitting summary."""

import requests
from prometheus_test import Context


async def prepare(context: Context):
    """Prepare for submitting summary."""
    staking_key = context.env.get("WORKER_ID")
    pr_url = await context.storeGet(f"pr-{staking_key}")

    return {
        "staking_key": staking_key,
        "round_number": context.round_number,
        "pr_url": pr_url,
        "github_username": context.env.get("GITHUB_USERNAME"),
    }


async def execute(context: Context, prepare_data: dict):
    """Execute summary submission test."""
    staking_key = prepare_data["staking_key"]
    round_number = prepare_data["round_number"]
    pr_url = prepare_data["pr_url"]
    github_username = prepare_data["github_username"]

    # Mock response for submission
    response = requests.post(
        "http://localhost:5000/api/summarizer/submit",
        json={
            "taskId": context.config.task_id,
            "roundNumber": round_number,
            "prUrl": pr_url,
            "stakingKey": staking_key,
            "githubUsername": github_username,
        },
    )

    if response.status_code != 200:
        raise Exception(f"Failed to submit summary: {response.text}")

    result = response.json()
    if not result.get("success"):
        raise Exception("Failed to submit summary")

    # Store submission data for audit
    await context.storeSet(
        f"submission-{staking_key}",
        {
            "cid": result.get("data", {}).get("cid"),
            "pr_url": pr_url,
            "github_username": github_username,
        },
    )

    return True
