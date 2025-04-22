"""Script to analyze test failures using Claude."""

import subprocess
from dotenv import load_dotenv
from test_parser import send_test_data_to_claude


def main():
    """Run the tests and analyze any failures."""
    # Load environment variables
    load_dotenv()

    # Run the failing test and capture output
    result = subprocess.run(
        ["pytest", "test_test_parser.py", "-v"],
        capture_output=True,
        text=True,
        check=False,
    )

    # Send the output to Claude
    test_data = {
        "test_name": "unknown",  # We'll let Claude figure this out
        "test_file": "unknown",  # We'll let Claude figure this out
        "error_message": "unknown",  # We'll let Claude figure this out
        "full_output": result.stdout + result.stderr,
    }

    response = send_test_data_to_claude(test_data)
    print("\nClaude's Analysis:")
    print("=================")
    print(response)


if __name__ == "__main__":
    main()
