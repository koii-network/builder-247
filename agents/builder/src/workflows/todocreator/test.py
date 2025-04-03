"""Todo creator workflow execution."""

import os
from src.workflows.base import WorkflowTest
from src.workflows.todocreator.workflow import TodoCreatorWorkflow
from src.workflows.todocreator.prompts import PROMPTS
from typing import List


class TodoCreatorTest(WorkflowTest):
    def __init__(self):
        super().__init__(
            description="Create tasks from a feature specification for a GitHub repository",
            additional_arguments={
                "repo": {
                    "type": str,
                    "required": True,
                    "help": "GitHub repository URL (e.g., https://github.com/owner/repo)",
                },
                "feature-spec": {
                    "type": str,
                    "required": True,
                    "help": "Description of the feature to implement",
                },
                "output": {
                    "type": str,
                    "default": "todos.csv",
                    "help": "Output CSV file path (default: todos.csv)",
                },
            },
            prompts=PROMPTS,
        )

    def _setup(
        self,
        github_token_env_var: str = "GITHUB_TOKEN",
        github_username_env_var: str = "GITHUB_USERNAME",
        additional_env_vars: List[str] = None,
    ):
        """Set up todo creator workflow context.

        Args:
            github_token_env_var: Name of env var containing GitHub token
            github_username_env_var: Name of env var containing GitHub username
            additional_env_vars: Additional required environment variables
        """
        # Combine GitHub env vars with any additional required vars
        required_env_vars = [github_token_env_var, github_username_env_var, "DATA_DIR"]
        if additional_env_vars:
            required_env_vars.extend(additional_env_vars)

        super()._setup(required_env_vars=required_env_vars)

        # Create workflow instance
        self.workflow = TodoCreatorWorkflow(
            client=self.client,
            prompts=self.prompts,
            repo_url=self.args.repo,
            feature_spec=self.args.feature_spec,
            output_csv_path=self.args.output,
            github_token=os.getenv(github_token_env_var),
            github_username=os.getenv(github_username_env_var),
        )

    def _run(self):
        """Run the todo creator workflow."""
        result = self.workflow.run()

        if not result or not result.get("success"):
            raise Exception("Todo creator workflow failed")

        # Verify the file exists
        output_csv = result["data"].get("output_csv", "")
        if output_csv and os.path.exists(output_csv):
            print(f"Created {result['data'].get('task_count', 0)} tasks")
            print(f"Results saved to {output_csv}")
        else:
            # Check alternative path in data directory
            file_name = os.path.basename(self.args.output)
            alternative_path = os.path.join(os.environ["DATA_DIR"], file_name)

            if os.path.exists(alternative_path):
                print(f"Created {result['data'].get('task_count', 0)} tasks")
                print(f"Results saved to {alternative_path}")
            else:
                raise Exception(
                    f"Todo creator workflow completed but output file was not created. "
                    f"Expected at: {output_csv} or {alternative_path}"
                )

        return result
