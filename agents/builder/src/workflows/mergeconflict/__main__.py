"""Main script for merge conflict resolution."""

import os
import sys
import argparse
from dotenv import load_dotenv
from github import Github
from src.utils.logging import log_error
from src.workflows.utils import repository_context
from src.clients import setup_client
from src.workflows.mergeconflict.workflow import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS


def create_consolidation_pr(upstream_repo, fork_url, branch, merged_prs):
    """Create a PR to upstream with all merged changes."""
    # Get our fork's owner from the workflow's fork URL
    gh = Github(os.environ["MERGE_GITHUB_TOKEN"])
    our_user = gh.get_user()
    our_fork_owner = our_user.login

    # Create PR with list of merged PRs in the body
    pr_body = "This PR consolidates the following PRs from the aggregator fork:\n\n"
    for pr_num in merged_prs:
        pr_url = f"{fork_url}/pull/{pr_num}"
        pr_body += f"- {pr_url}\n"

    pr = upstream_repo.create_pull(
        title=f"Consolidate PRs from {our_fork_owner}",
        body=pr_body,
        head=f"{our_fork_owner}:{branch}",  # Use our fork as the head
        base="main",
    )

    return pr.html_url


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


def main():
    """Main entry point."""
    try:
        # Load environment variables
        load_dotenv()
        github_token = os.environ["MERGE_GITHUB_TOKEN"]
        github_username = os.environ["GITHUB_USERNAME"]

        # Parse arguments
        args = parse_args()

        # Extract owner/repo from source URL
        parts = args.source.strip("/").split("/")
        if len(parts) < 2:
            print("Invalid repository URL format. Use https://github.com/owner/repo")
            sys.exit(1)
        owner, repo = parts[-2:]

        # Set up repository
        repo_url = f"https://github.com/{owner}/{repo}"
        fork_name = f"{repo}-{owner}"
        with repository_context(
            repo_url,
            github_token=github_token,
            fork_name=fork_name,
        ):
            # Get upstream repo info
            gh = Github(github_token)
            source_fork = gh.get_repo(f"{owner}/{repo}")
            if not source_fork.fork:
                raise Exception("Source repository is not a fork")

            upstream_repo = source_fork.parent
            print(f"Found upstream repository: {upstream_repo.html_url}")

            # Get list of open PRs
            open_prs = list(source_fork.get_pulls(state="open", base=args.branch))
            print(f"Found {len(open_prs)} open PRs")

            if not open_prs:
                print("No open PRs to consolidate")
                return

            # Sort PRs by creation date (oldest first)
            open_prs.sort(key=lambda pr: pr.created_at)

            # Initialize workflow
            client = setup_client("anthropic")
            workflow = MergeConflictWorkflow(
                client=client,
                prompts=PROMPTS,
                source_fork_url=repo_url,
                source_branch=args.branch,
                is_source_fork_owner=owner == github_username,
                github_token=github_token,
                github_username=github_username,
            )

            # Run workflow to process and consolidate PRs
            result = workflow.run()
            if result:
                print(f"Successfully created consolidated PR: {result}")
            else:
                print("No PRs were processed or PR creation failed")

    except Exception as e:
        log_error(e, "Error in merge conflict workflow")
        sys.exit(1)


if __name__ == "__main__":
    main()
