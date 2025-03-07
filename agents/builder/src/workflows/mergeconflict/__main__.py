"""Command-line interface for the merge conflict resolver workflow."""

import sys
import argparse
from dotenv import load_dotenv
from github import Github
from src.clients import setup_client
from src.workflows.mergeconflict import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS
from src.workflows.utils import setup_repository
import os


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Merge conflict resolver workflow")
    parser.add_argument(
        "--source",
        required=True,
        help="URL of the fork containing the PRs to merge",
    )
    parser.add_argument(
        "--branch",
        required=True,
        help="Name of the branch containing PRs to merge (e.g., main)",
    )
    return parser.parse_args()


def create_consolidation_pr(upstream_repo, fork_url, branch, merged_prs):
    """Create a PR to upstream with all merged changes."""
    fork_parts = fork_url.strip("/").split("/")
    fork_owner = fork_parts[-2]
    fork_repo = fork_parts[-1]

    # Create PR with list of merged PRs in the body
    pr_body = "This PR consolidates the following PRs from the aggregator fork:\n\n"
    for pr_num in merged_prs:
        pr_url = f"https://github.com/{fork_owner}/{fork_repo}/pull/{pr_num}"
        pr_body += f"- {pr_url}\n"

    pr = upstream_repo.create_pull(
        title=f"Consolidate PRs from {fork_owner}",
        body=pr_body,
        head=f"{fork_owner}:{branch}",
        base="main",
    )

    return pr.html_url


def main():
    """Run the merge conflict resolver workflow."""
    # Load environment variables from .env file
    load_dotenv()

    # Parse command line arguments
    args = parse_args()

    # Initialize Claude client
    client = setup_client("anthropic")

    # Extract owner/repo from source fork URL
    source_parts = args.source.strip("/").split("/")
    source_owner = source_parts[-2]
    source_repo = source_parts[-1]

    # Get source fork and its upstream repo
    gh = Github(os.environ["GITHUB_TOKEN"])
    source_fork = gh.get_repo(f"{source_owner}/{source_repo}")
    if not source_fork.fork:
        print("Error: Source repository is not a fork")
        return 1

    upstream_repo = source_fork.parent
    print(f"Found upstream repository: {upstream_repo.html_url}")

    # Create and set up our fork
    print("\n=== SETTING UP REPOSITORY ===")
    setup_result = setup_repository(args.source)
    if not setup_result["success"]:
        print(
            f"Error setting up repository: {setup_result.get('message', 'Unknown error')}"
        )
        return 1

    our_fork_url = setup_result["data"]["fork_url"]
    print(f"Using fork: {our_fork_url}")

    # Get list of open PRs from source fork
    open_prs = list(source_fork.get_pulls(state="open", base=args.branch))
    # Sort PRs by creation date (oldest first)
    open_prs.sort(key=lambda pr: pr.created_at)
    print(f"\nFound {len(open_prs)} open PRs to process")

    # Process each PR
    all_merged_prs = []
    all_failed_prs = []

    for pr in open_prs:
        print(f"\n=== PROCESSING PR #{pr.number} ===")
        workflow = MergeConflictWorkflow(
            client=client,
            prompts=PROMPTS,
            fork_url=args.source,
            target_branch=args.branch,
            pr_url=pr.html_url,
        )

        result = workflow.run()

        if result and result.get("success"):
            merged = result["data"].get("merged_prs", [])
            failed = result["data"].get("failed_prs", [])
            all_merged_prs.extend(merged)
            all_failed_prs.extend(failed)

    # Print summary
    print("\n=== MERGE SUMMARY ===")
    print(f"Total PRs processed: {len(open_prs)}")
    print(f"Successfully merged: {len(all_merged_prs)}")
    print(f"Failed to merge: {len(all_failed_prs)}")

    if all_merged_prs:
        print("\n=== CREATING CONSOLIDATION PR ===")
        pr_url = create_consolidation_pr(
            upstream_repo, args.source, args.branch, all_merged_prs
        )
        print(f"Created consolidation PR: {pr_url}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
