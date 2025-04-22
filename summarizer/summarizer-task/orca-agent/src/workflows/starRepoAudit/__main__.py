"""Entry point for the todo creator workflow."""

import sys
import os
import argparse
from dotenv import load_dotenv
from src.workflows.starRepoAudit.workflow import StarRepoAuditWorkflow
from src.workflows.starRepoAudit.prompts import PROMPTS
from prometheus_swarm.clients import setup_client

# Load environment variables
load_dotenv()


def main():
    """Run the todo creator workflow."""
    parser = argparse.ArgumentParser(
        description="Create tasks from a feature specification for a GitHub repository"
    )
    parser.add_argument(
        "--repo",
        type=str,
        required=True,
        help="GitHub repository URL (e.g., https://github.com/owner/repo)",
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

    # Run the todo creator workflow
    workflow = StarRepoAuditWorkflow(
        client=client,
        prompts=PROMPTS,
        repo_url=args.repo,
        github_username="HermanL02",
    )


    result = workflow.run()
    if not result or not result.get("success"):
        print("Todo creator workflow failed")
        sys.exit(1)
    




if __name__ == "__main__":
    main()
