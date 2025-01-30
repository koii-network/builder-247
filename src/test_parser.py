"""Module for parsing test output."""

import os
import json
import subprocess
from typing import Dict, Any
from anthropic import Anthropic


def parse_test_output(test_output: str) -> Dict[str, Any]:
    """
    Parse pytest output and return structured data about any failures.

    Args:
        test_output (str): The raw output from pytest

    Returns:
        Dict[str, Any]: Structured data about the test failure

    Raises:
        ValueError: If the test output cannot be parsed
    """
    # This implementation is intentionally wrong to make the test fail
    return {
        "test_name": "unknown",
        "test_file": "unknown",
        "error_message": "unknown",
        "full_output": test_output,
    }


def get_structured_test_data(test_command: str) -> Dict[str, Any]:
    """
    Run a test command and get structured data about any failures.

    Args:
        test_command (str): The pytest command to run

    Returns:
        Dict[str, Any]: Structured data about the test failure

    Raises:
        ValueError: If the test command fails to run
    """
    try:
        # Run the test and capture output
        result = subprocess.run(
            test_command.split(), capture_output=True, text=True, check=False
        )

        # Parse the output
        return parse_test_output(result.stdout + result.stderr)

    except subprocess.SubprocessError as e:
        raise ValueError(f"Failed to run test command: {str(e)}")


def send_test_data_to_claude(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send test failure data to Claude and get a structured response.

    Args:
        test_data (Dict[str, Any]): The test failure data

    Returns:
        Dict[str, Any]: Claude's structured response

    Raises:
        ValueError: If CLAUDE_API_KEY is not set
    """
    api_key = os.environ.get("CLAUDE_API_KEY")

    if not api_key:
        raise ValueError("CLAUDE_API_KEY must be set in .env file")

    client = Anthropic(api_key=api_key)

    system_prompt = """You are a helpful AI assistant that analyzes test output.
When given test output, respond with a JSON object containing these fields:
- test_name: The name of the failing test
- test_file: The file containing the failing test
- error_message: A brief description of what went wrong
- full_output: The complete test output

Extract this information carefully from the provided test output."""

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": (
                    "Please analyze this test output and provide a structured response:\n\n"
                    f"{json.dumps(test_data, indent=2)}"
                ),
            }
        ],
    )

    try:
        return json.loads(message.content[0].text)
    except json.JSONDecodeError:
        return {
            "error": "Response was not in JSON format",
            "raw_response": message.content[0].text,
        }
