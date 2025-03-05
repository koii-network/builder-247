"""Entry point for the bug finder workflow."""

import sys
import os
import argparse
from dotenv import load_dotenv
from src.workflows.bugfinder.workflow import BugFinderWorkflow
from src.workflows.bugfinder.prompts import PROMPTS
from src.clients import setup_client

# Load environment variables
load_dotenv()


def main():
    """Run the bug finder workflow."""
    parser = argparse.ArgumentParser(description="Find bugs in a GitHub repository")
    parser.add_argument(
        "--repo",
        type=str,
        required=True,
        help="GitHub repository URL (e.g., https://github.com/owner/repo)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="bugs.csv",
        help="Output CSV file path (default: bugs.csv)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic",
        choices=["anthropic", "openai", "xai"],
        help="Model provider to use (default: anthropic)",
    )
    args = parser.parse_args()

    # Initialize client
    client = setup_client(args.model)

    # Run the bug finder workflow
    workflow = BugFinderWorkflow(
        client=client,
        prompts=PROMPTS,
        repo_url=args.repo,
        output_csv_path=args.output,
    )

    result = workflow.run()
    if not result or not result.get("success"):
        print("Bug finder workflow failed")
        sys.exit(1)

    # Verify the file exists in the project's data directory
    output_csv = result["data"].get("output_csv", "")

    # If the file exists at the path returned by the tool, use that
    if output_csv and os.path.exists(output_csv):
        print("Bug finder workflow completed successfully")
        print(f"Found {result['data'].get('issue_count', 0)} issues")
        print(f"Results saved to {output_csv}")
    else:
        # If not found at the returned path, check if it's in the project's data directory
        project_data_dir = "/home/laura/git/github/builder-247/data"
        file_name = os.path.basename(args.output)
        alternative_path = os.path.join(project_data_dir, file_name)

        if os.path.exists(alternative_path):
            print("Bug finder workflow completed successfully")
            print(f"Found {result['data'].get('issue_count', 0)} issues")
            print(f"Results saved to {alternative_path}")
        else:
            print("Bug finder workflow completed but the output file was not created")
            print(f"Expected file at: {output_csv}")
            print(f"Also checked: {alternative_path}")
            sys.exit(1)


if __name__ == "__main__":
    main()
