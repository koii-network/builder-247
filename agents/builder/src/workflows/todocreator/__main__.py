"""Entry point for the todo creator workflow."""

import sys
import os
import argparse
from dotenv import load_dotenv
from src.workflows.todocreator.workflow import TodoCreatorWorkflow
from src.workflows.todocreator.prompts import PROMPTS
from src.clients import setup_client

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
        "--feature-spec",
        type=str,
        required=True,
        help="Description of the feature to implement",
    )
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
    args = parser.parse_args()

    # Initialize client
    client = setup_client(args.model)

    # Run the todo creator workflow
    workflow = TodoCreatorWorkflow(
        client=client,
        prompts=PROMPTS,
        repo_url=args.repo,
        feature_spec=args.feature_spec,
        output_json_path=args.output,
    )

    result = workflow.run()
    if not result or not result.get("success"):
        print("Todo creator workflow failed")
        sys.exit(1)

    # Verify the file exists in the project's data directory
    output_json = result["data"].get("output_json", "")

    # If the file exists at the path returned by the tool, use that
    if output_json and os.path.exists(output_json):
        print("Todo creator workflow completed successfully")
        print(f"Created {result['data'].get('task_count', 0)} tasks")
        print(f"Results saved to {output_json}")
        if result["data"].get("validation_issues"):
            print("\nValidation issues found:")
            for issue in result["data"]["validation_issues"]:
                print(f"- {issue}")
    else:
        # If not found at the returned path, check if it's in the project's data directory
        project_data_dir = "/home/herman/Downloads/builder-247/data"
        file_name = os.path.basename(args.output)
        alternative_path = os.path.join(project_data_dir, file_name)

        if os.path.exists(alternative_path):
            print("Todo creator workflow completed successfully")
            print(f"Created {result['data'].get('task_count', 0)} tasks")
            print(f"Results saved to {alternative_path}")
            if result["data"].get("validation_issues"):
                print("\nValidation issues found:")
                for issue in result["data"]["validation_issues"]:
                    print(f"- {issue}")
        else:
            print("Todo creator workflow completed but the output file was not created")
            print(f"Expected file at: {output_json}")
            print(f"Also checked: {alternative_path}")
            sys.exit(1)


if __name__ == "__main__":
    main()
