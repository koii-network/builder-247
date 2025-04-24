"""Test stage for validating API keys."""

import requests
from prometheus_test import Context


async def prepare(context: Context):
    """Prepare for API key validation test."""
    return {
        "api_key": context.env.get("ANTHROPIC_API_KEY"),
    }


async def execute(context: Context, prepare_data: dict):
    """Execute API key validation test."""
    api_key = prepare_data["api_key"]

    # Mock response for Anthropic API validation
    response = requests.post(
        "http://localhost:5000/api/summarizer/validate-api-key",
        json={"api_key": api_key},
    )

    if response.status_code != 200:
        raise Exception(f"API key validation failed: {response.text}")

    result = response.json()
    if not result.get("valid"):
        raise Exception("API key is not valid")

    return True
