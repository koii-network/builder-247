"""Command-line interface for the merge conflict resolver workflow."""

import sys
import argparse
from dotenv import load_dotenv
from src.clients import setup_client
from src.workflows.mergeconflict import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Merge conflict resolver workflow")
    parser.add_argument(
        "--repo-url",
        required=True,
        help="URL of the GitHub repository (e.g., https://github.com/owner/repo)",
    )
    parser.add_argument(
        "--branch",
        required=True,
        help="Name of the branch to merge PRs into (e.g., main)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit the number of PRs to process (0 means no limit)",
    )
    return parser.parse_args()


def main():
    """Run the merge conflict resolver workflow."""
    # Load environment variables from .env file
    load_dotenv()

    # Parse command line arguments
    args = parse_args()

    # Initialize Claude client
    client = setup_client("anthropic")

    # Use the workflow to process all PRs with the limit
    workflow = MergeConflictWorkflow(
        client=client,
        prompts=PROMPTS,
        repo_url=args.repo_url,
        target_branch=args.branch,
        pr_limit=args.limit,
    )

    result = workflow.run()

    # Print summary
    print("\n=== MERGE SUMMARY ===")
    if result and result.get("success"):
        merged_prs = result["data"].get("merged_prs", [])
        failed_prs = result["data"].get("failed_prs", [])

        print(f"Successfully merged {len(merged_prs)} PRs")
        if merged_prs:
            print("Merged PRs:", ", ".join(f"#{pr}" for pr in merged_prs))
        if failed_prs:
            print(f"Failed to merge {len(failed_prs)} PRs")
            print("Failed PRs:", ", ".join(f"#{pr}" for pr in failed_prs))
    else:
        error_message = (
            result.get("message", "Unknown error")
            if result
            else "Workflow returned no result"
        )
        print(f"Error running workflow: {error_message}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
