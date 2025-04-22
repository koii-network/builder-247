"""Entry point for the todo creator workflow."""

import sys
import argparse
from dotenv import load_dotenv
from src.workflows.repoClassifier.workflow import RepoClassifierWorkflow
from src.workflows.repoClassifier.prompts import PROMPTS
from prometheus_swarm.clients import setup_client

# Load environment variables
load_dotenv()


def main():
    """Run the todo creator workflow."""
    parser = argparse.ArgumentParser(
        description="Classify a GitHub repository"
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
    workflow = RepoClassifierWorkflow(
        client=client,
        prompts=PROMPTS,
        repo_url=args.repo,
    )

    result = workflow.run()
    if not result or not result.get("success"):
        print("Repo classifier workflow failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
