"""Test stage for validating GitHub credentials."""

import requests
from prometheus_test import Context


async def prepare(context: Context):
    """Prepare for GitHub validation test."""
    return {
        "github_username": context.env.get("GITHUB_USERNAME"),
        "github_token": context.env.get("GITHUB_TOKEN"),
    }


async def execute(context: Context, prepare_data: dict):
    """Execute GitHub validation test."""
    username = prepare_data["github_username"]
    token = prepare_data["github_token"]

    # Mock response for GitHub validation
    response = requests.post(
        "http://localhost:5000/api/builder/summarizer/validate-github",
        json={"username": username, "token": token},
    )

    if response.status_code != 200:
        raise Exception(f"GitHub validation failed: {response.text}")

    result = response.json()
    if not result.get("valid"):
        raise Exception("GitHub credentials are not valid")

    return True
