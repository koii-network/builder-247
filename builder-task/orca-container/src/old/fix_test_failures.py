"""Script to analyze and fix test failures using Claude."""

import os
import json
import subprocess
from typing import Dict, Any, List
from dotenv import load_dotenv
from anthropic import Anthropic


def get_test_output() -> str:
    """Run the tests and get the output."""
    result = subprocess.run(
        ["pytest", "test_string_operations.py", "-v"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout + result.stderr


def get_fix_from_claude(test_output: str) -> List[Dict[str, Any]]:
    """
    Send test output to Claude and get suggested fixes.

    Args:
        test_output (str): The test output containing failures

    Returns:
        List[Dict[str, Any]]: List of fixes suggested by Claude
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY must be set in .env file")

    client = Anthropic(api_key=api_key)

    system_prompt = """You are a helpful AI assistant that analyzes test failures and suggests fixes.
When given test output, respond with a JSON array containing objects with these fields for each failing test:
- test_name: The name of the failing test
- test_file: The file containing the failing test
- error_message: A brief description of what went wrong
- fix_file: The name of the file that needs to be fixed
- fix_content: The complete content of the file after applying the fix

Analyze the test output carefully to determine whether the error is in the test itself or in the implementation.
Provide the complete fixed file content, not just the changes.
Make sure to format your response as a valid JSON array."""

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Please analyze these test failures and provide fixes:\n\n{test_output}",
            }
        ],
    )

    try:
        return json.loads(message.content[0].text)
    except json.JSONDecodeError:
        print("Error parsing Claude's response as JSON:")
        print(message.content[0].text)
        return []


def apply_fixes(fixes: List[Dict[str, Any]]) -> None:
    """
    Apply the fixes suggested by Claude.

    Args:
        fixes (List[Dict[str, Any]]): The fixes suggested by Claude
    """
    if not fixes:
        print("No valid fixes found in Claude's response")
        return

    for fix in fixes:
        fix_file = fix.get("fix_file")
        fix_content = fix.get("fix_content")

        if fix_file and fix_content:
            print(f"\nApplying fix to {fix_file}...")
            with open(fix_file, "w") as f:
                f.write(fix_content)
            print(f"Fix applied to {fix_file}")


def main():
    """Run the tests, get fixes from Claude, and apply them."""
    # Load environment variables
    load_dotenv()

    # Get test output
    print("Running tests...")
    test_output = get_test_output()
    print("\nTest output:")
    print("============")
    print(test_output)

    # Get fixes from Claude
    print("\nGetting fixes from Claude...")
    fixes = get_fix_from_claude(test_output)

    # Apply fixes
    print("\nApplying fixes...")
    apply_fixes(fixes)

    # Run tests again to verify fixes
    print("\nVerifying fixes...")
    final_output = get_test_output()
    print("\nFinal test output:")
    print("=================")
    print(final_output)


if __name__ == "__main__":
    main()
