"""Entry point for the todo creator workflow."""

import sys
import os
import argparse
from dotenv import load_dotenv
from src.workflows.todocreator.workflow import TodoCreatorWorkflow
from src.workflows.todocreator.prompts import PROMPTS
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
    # parser.add_argument(
    #     "--feature-spec",
    #     type=str,
    #     required=True,
    #     help="Description of the feature to implement",
    # )
    parser.add_argument(
        "--output",
        type=str,
        default="todos.json",
        help="Output JSON file path (default: todos.json)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic",
        choices=["anthropic", "openai", "xai"],
        help="Model provider to use (default: anthropic)",
    )
    parser.add_argument(
        "--issue-spec",
        type=str,
        required=True,
        help="Description of the issue to implement",
    )
    args = parser.parse_args()

    # Initialize client
    client = setup_client(args.model)

    # Run the todo creator workflow
    workflow = TodoCreatorWorkflow(
        client=client,
        prompts=PROMPTS,
        repo_url=args.repo,
        # feature_spec=args.feature_spec,
        issue_spec=args.issue_spec,
    )


    result = workflow.run()
    if not result or not result.get("success"):
        print("Todo creator workflow failed")
        sys.exit(1)
    




if __name__ == "__main__":
    main()
