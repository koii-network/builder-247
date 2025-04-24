"""Test stage for fetching summarizer todo."""

import requests
from prometheus_test import Context


async def prepare(context: Context):
    """Prepare for fetching summarizer todo."""
    return {
        "staking_key": context.env.get("WORKER_ID"),
        "round_number": context.round_number,
    }


async def execute(context: Context, prepare_data: dict):
    """Execute fetch summarizer todo test."""
    staking_key = prepare_data["staking_key"]
    round_number = prepare_data["round_number"]

    # Mock response for fetching todo
    response = requests.post(
        "http://localhost:5000/api/summarizer/fetch-summarizer-todo",
        json={
            "stakingKey": staking_key,
            "roundNumber": round_number,
        },
    )

    if response.status_code != 200:
        raise Exception(f"Failed to fetch summarizer todo: {response.text}")

    result = response.json()
    if not result.get("success"):
        raise Exception("Failed to fetch summarizer todo")

    # Store todo data for next steps
    await context.storeSet(f"todo-{staking_key}", result.get("data"))

    return True
