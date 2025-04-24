"""Test stage for generating repository summary."""

import requests
from prometheus_test import Context


async def prepare(context: Context):
    """Prepare for generating summary."""
    staking_key = context.env.get("WORKER_ID")
    todo = await context.storeGet(f"todo-{staking_key}")

    return {
        "staking_key": staking_key,
        "round_number": context.round_number,
        "repo_owner": todo.get("repo_owner"),
        "repo_name": todo.get("repo_name"),
    }


async def execute(context: Context, prepare_data: dict):
    """Execute summary generation test."""
    staking_key = prepare_data["staking_key"]
    round_number = prepare_data["round_number"]
    repo_owner = prepare_data["repo_owner"]
    repo_name = prepare_data["repo_name"]

    # Mock response for repo summary generation
    response = requests.post(
        "http://localhost:5000/api/summarizer/generate-summary",
        json={
            "taskId": context.config.task_id,
            "round_number": str(round_number),
            "repo_url": f"https://github.com/{repo_owner}/{repo_name}",
        },
    )

    if response.status_code != 200:
        raise Exception(f"Failed to generate summary: {response.text}")

    result = response.json()
    if not result.get("success"):
        raise Exception("Failed to generate summary")

    # Store PR URL for next steps
    await context.storeSet(f"pr-{staking_key}", result.get("data", {}).get("pr_url"))

    return True
