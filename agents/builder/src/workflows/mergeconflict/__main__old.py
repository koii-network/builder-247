"""Main script for merge conflict resolution."""

import os
import sys
import argparse
from dotenv import load_dotenv
from github import Github
from src.utils.logging import log_error
from src.workflows.utils import repository_context, get_fork_name
from src.clients import setup_client
from src.workflows.mergeconflict.workflow import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS


def create_consolidation_pr(
    upstream_repo, source_owner, source_repo, branch, merged_prs
):
    """Create a PR to upstream with all merged changes.

    Args:
        upstream_repo: GitHub repo object for the upstream repo
        source_owner: Owner of the original source fork
        source_repo: Name of the original source fork
        branch: Branch name
        merged_prs: List of PR numbers that were merged
    """
    # Get our fork's owner and repo name
    gh = Github(os.environ["MERGE_GITHUB_TOKEN"])
    our_user = gh.get_user()
    our_fork_owner = our_user.login

    # Create PR with list of merged PRs in the body
    pr_body = "This PR consolidates the following PRs from the aggregator fork:\n\n"
    for pr_num in merged_prs:
        # Use the original source fork URL for PR links since that's where the PRs are
        pr_url = f"https://github.com/{source_owner}/{source_repo}/pull/{pr_num}"
        pr_body += f"- {pr_url}\n"

    pr = upstream_repo.create_pull(
        title=f"Consolidate PRs from {source_owner}",
        body=pr_body,
        head=f"{our_fork_owner}:{branch}",  # Use our uniquely named fork as the head
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
        source_owner, source_repo = parts[-2:]  # Original fork's owner and name

        # Set up repository with unique fork name
        repo_url = f"https://github.com/{source_owner}/{source_repo}"
        gh = Github(github_token)
        fork_name = get_fork_name(source_owner, repo_url, github=gh)
        with repository_context(
            repo_url,
            github_token=github_token,
            fork_name=fork_name,
        ):
            # Get upstream repo info using original source fork
            source_fork = gh.get_repo(f"{source_owner}/{source_repo}")
            if not source_fork.fork:
                raise Exception("Source repository is not a fork")

            upstream_repo = source_fork.parent
            print(f"Found upstream repository: {upstream_repo.html_url}")

            # Get list of open PRs from original source fork
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
                is_source_fork_owner=source_owner == github_username,
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
