#!/usr/bin/env python3
"""
Script to merge all PRs into the main branch, resolving conflicts as they arise.

This script uses the merge conflict resolver workflow to handle conflicts.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from github import Github
from src.clients.anthropic_client import AnthropicClient
from src.workflows.mergeconflict import RemoteMergeConflictWorkflow, PROMPTS


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Merge all PRs into the main branch, resolving conflicts as they arise."
    )
    parser.add_argument(
        "--repo-url",
        required=True,
        help="URL of the GitHub repository (e.g., https://github.com/owner/repo)",
    )
    parser.add_argument(
        "--target-branch",
        default="main",
        help="Name of the target branch to merge into (defaults to 'main')",
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (can also be set via ANTHROPIC_API_KEY environment variable)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually merging PRs",
    )
    parser.add_argument(
        "--skip-merged",
        action="store_true",
        help="Skip PRs that have already been merged",
    )
    parser.add_argument(
        "--skip-closed",
        action="store_true",
        help="Skip PRs that have been closed without merging",
    )
    return parser.parse_args()


def get_repo_info(repo_url):
    """Extract owner and repo name from URL."""
    # URL format: https://github.com/owner/repo
    parts = repo_url.strip("/").split("/")
    repo_owner = parts[-2]
    repo_name = parts[-1]
    return repo_owner, repo_name


def main():
    """Run the script."""
    # Load environment variables from .env file
    load_dotenv()

    # Parse command line arguments
    args = parse_args()

    # Set API key from arguments or environment variable
    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: Anthropic API key not provided.")
        print(
            "Please provide it via --api-key or set ANTHROPIC_API_KEY environment variable."
        )
        sys.exit(1)

    # Check for required environment variables
    if not os.getenv("GITHUB_TOKEN"):
        print("Error: GITHUB_TOKEN environment variable not set.")
        print("Please set it in your .env file or environment.")
        sys.exit(1)

    if not os.getenv("GITHUB_USERNAME"):
        print("Error: GITHUB_USERNAME environment variable not set.")
        print("Please set it in your .env file or environment.")
        sys.exit(1)

    # Extract owner and repo name from URL
    repo_owner, repo_name = get_repo_info(args.repo_url)

    # Initialize GitHub client
    gh = Github(os.getenv("GITHUB_TOKEN"))
    repo = gh.get_repo(f"{repo_owner}/{repo_name}")

    # Get all PRs
    print(f"Fetching PRs for {repo_owner}/{repo_name}...")

    # Filter PRs based on command line arguments
    prs = []
    for pr in repo.get_pulls(state="all"):
        if pr.base.ref != args.target_branch:
            continue

        if args.skip_merged and pr.merged:
            print(f"Skipping PR #{pr.number} (already merged): {pr.title}")
            continue

        if args.skip_closed and pr.state == "closed" and not pr.merged:
            print(f"Skipping PR #{pr.number} (closed without merging): {pr.title}")
            continue

        if pr.state == "open" or (
            pr.state == "closed" and not pr.merged and not args.skip_closed
        ):
            prs.append(pr)

    print(f"Found {len(prs)} PRs to process")

    # Initialize Claude client
    client = AnthropicClient(api_key=api_key)

    # Process each PR
    for i, pr in enumerate(prs):
        print(f"\n[{i+1}/{len(prs)}] Processing PR #{pr.number}: {pr.title}")
        print(f"Source branch: {pr.head.ref}")
        print(f"Target branch: {pr.base.ref}")

        if args.dry_run:
            print("Dry run: Skipping actual merge")
            continue

        try:
            # Try to merge the PR directly first
            try:
                if pr.mergeable:
                    print(f"PR #{pr.number} can be merged directly")
                    pr.merge(merge_method="merge")
                    print(f"Successfully merged PR #{pr.number}")
                    continue
            except Exception as e:
                print(f"Could not merge PR #{pr.number} directly: {str(e)}")

            # If direct merge fails, use the merge conflict resolver workflow
            print(f"Resolving conflicts for PR #{pr.number}")

            workflow = MergeConflictWorkflow(
                client=client,
                prompts=PROMPTS,
                repo_url=args.repo_url,
                source_branch=pr.head.ref,
                target_branch=pr.base.ref,
                pr_number=pr.number,
            )

            result = workflow.run()

            if result and result.get("success"):
                conflicts = result["data"].get("conflicts", [])
                resolved = result["data"].get("resolved_conflicts", [])

                print(f"Found {len(conflicts)} conflicts")
                print(f"Successfully resolved {len(resolved)} conflicts")
                print(f"Conflicts resolved and merged for PR #{pr.number}")
            else:
                error_message = (
                    result.get("message", "Unknown error")
                    if result
                    else "Workflow returned no result"
                )
                print(f"Error resolving conflicts for PR #{pr.number}: {error_message}")
        except Exception as e:
            print(f"Error processing PR #{pr.number}: {str(e)}")

    print("\nAll PRs processed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
