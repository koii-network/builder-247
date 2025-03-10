"""Command-line interface for the merge conflict resolver workflow."""

import sys
import argparse
from dotenv import load_dotenv
from github import Github
from src.clients import setup_client
from src.workflows.mergeconflict import RemoteMergeConflictWorkflow, LocalMergeConflictWorkflow
from src.workflows.mergeconflict.prompts import REMOTE_PROMPTS, LOCAL_PROMPTS
from src.workflows.utils import setup_repository
import os





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


def remote_pr_logic():
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
    gh = Github(os.environ["MERGE_GITHUB_TOKEN"])
    source_fork = gh.get_repo(f"{source_owner}/{source_repo}")
    if not source_fork.fork:
        print("Error: Source repository is not a fork")
        return 1

    upstream_repo = source_fork.parent
    print(f"Found upstream repository: {upstream_repo.html_url}")

    # Create and set up our fork
    print("\n=== SETTING UP REPOSITORY ===")
    setup_result = setup_repository(
        args.source, github_token=os.environ["MERGE_GITHUB_TOKEN"]
    )
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
        workflow = RemoteMergeConflictWorkflow(
            client=client,
            prompts=REMOTE_PROMPTS,
            fork_url=args.source,
            target_branch=args.branch,
            pr_url=pr.html_url,
            github_token=os.environ["MERGE_GITHUB_TOKEN"],
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





def local_pr_logic():
    """Run the merge conflict resolver workflow."""
    # Load environment variables from .env file
    load_dotenv()

    # Parse command line arguments
    args = parse_args()

    # Initialize Claude client
    client = setup_client("anthropic")

    # Use the workflow to process all PRs with the limit
    workflow = LocalMergeConflictWorkflow(
        client=client,
        prompts=LOCAL_PROMPTS,
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
        closed_prs = [pr for pr in failed_prs if result["data"].get("should_close")]
        error_prs = [pr for pr in failed_prs if pr not in closed_prs]
        total_prs = len(merged_prs) + len(failed_prs)

        print(f"Total PRs processed: {total_prs}")
        print(f"Successfully merged: {len(merged_prs)}")

        if closed_prs:
            print(f"Closed without merging: {len(closed_prs)}")
            print("Closed PRs:", ", ".join(f"#{pr}" for pr in closed_prs))

        if error_prs:
            print(f"Failed to process: {len(error_prs)}")
            print("Failed PRs:", ", ".join(f"#{pr}" for pr in error_prs))
    else:
        error_message = (
            result.get("message", "Unknown error")
            if result
            else "Workflow returned no result"
        )
        print(f"Error running workflow: {error_message}")

    return 0

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
    parser.add_argument(
        "--repo-url",
        required=True,
        help="URL of the GitHub repository (e.g., https://github.com/owner/repo)",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit the number of PRs to process (0 means no limit)",
    )
    return parser.parse_args()




if __name__ == "__main__":

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
    # Get Source Repo
    env_owner = os.environ["GITHUB_USERNAME"]
    if source_owner == env_owner:
        print("Local repo PR Logic Process Started")
        sys.exit(local_pr_logic())  # Local repo
    else:
        print("Remote repo PR Logic Process Started")
        sys.exit(remote_pr_logic())  # Remote repo
        
