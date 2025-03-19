"""Merge conflict workflow execution."""

from github import Github
from src.workflows.base import WorkflowExecution
from src.workflows.mergeconflict.workflow import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS
from typing import List
import os


class MergeConflictExecution(WorkflowExecution):
    def __init__(self):
        super().__init__(
            description="Merge conflict resolver workflow",
            additional_arguments={
                "source": {
                    "type": str,
                    "required": True,
                    "help": "URL of the fork containing the PRs to merge",
                },
                "branch": {
                    "type": str,
                    "required": True,
                    "help": "Name of the branch containing PRs to merge (e.g., main)",
                },
            },
        )
        self.workflow = None

    def _setup(
        self,
        github_token_env_var: str = "MERGE_GITHUB_TOKEN",
        github_username_env_var: str = "GITHUB_USERNAME",
        additional_env_vars: List[str] = None,
    ):
        """Set up merge conflict workflow context.

        Args:
            github_token_env_var: Name of env var containing GitHub token
            github_username_env_var: Name of env var containing GitHub username
            additional_env_vars: Additional required environment variables
        """
        # Combine GitHub env vars with any additional required vars
        required_env_vars = [github_token_env_var, github_username_env_var]
        if additional_env_vars:
            required_env_vars.extend(additional_env_vars)

        super()._setup(required_env_vars=required_env_vars, prompts=PROMPTS)

        repo_url = self.args.source
        source_owner, source_repo = self._parse_github_url(repo_url)

        # Get upstream repo info using original source fork
        gh = Github(os.getenv(github_token_env_var))
        source_fork = gh.get_repo(f"{source_owner}/{source_repo}")
        if not source_fork.fork:
            raise Exception("Source repository is not a fork")

        # Create workflow instance
        self.workflow = MergeConflictWorkflow(
            client=self.client,
            prompts=self.prompts,
            source_fork_url=repo_url,
            source_branch=self.args.branch,
            is_source_fork_owner=source_owner == os.getenv(github_username_env_var),
            github_token=os.getenv(github_token_env_var),
            github_username=os.getenv(github_username_env_var),
        )

    def _run(self):
        """Run the merge conflict workflow."""
        result = self.workflow.run()

        if result:
            print(f"Successfully created consolidated PR: {result}")
        else:
            raise Exception("No PRs were processed or PR creation failed")
