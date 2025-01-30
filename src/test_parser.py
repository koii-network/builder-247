"""Module for parsing test output."""

import os
import json
import subprocess
import re
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
    # Initialize default values
    result = {
        "test_name": "unknown",
        "test_file": "unknown",
        "error_message": "",
        "full_output": test_output,
    }

    # First try to find test name from the test run line
    test_run = re.search(r"(\w+\.py)::(\w+)\s+(?:FAILED|ERROR)", test_output)
    if test_run:
        result["test_file"] = test_run.group(1)
        result["test_name"] = test_run.group(2)

    # Look for detailed error in FAILURES section
    failure_section = re.search(r"=+ FAILURES =+\n(.+?)=+", test_output, re.DOTALL)
    if failure_section:
        # Extract error message including assertion details
        error_lines = []
        for line in failure_section.group(1).split('\n'):
            if line.startswith('E       '):
                error_lines.append(line.replace('E       ', ''))
        if error_lines:
            result["error_message"] = '\n'.join(error_lines)
            return result

    # If no detailed error found, look for summary error
    summary = re.search(r"FAILED .+? - (.+?)(?:\n|$)", test_output)
    if summary:
        result["error_message"] = summary.group(1)

    return result


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
