"""Merge conflict workflow execution."""

from github import Github
from prometheus_swarm.workflows.base import WorkflowExecution
from src.workflows.mergeconflict.workflow import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS
from typing import List
import os


class MergeConflictExecution(WorkflowExecution):
    def __init__(self):
        super().__init__(
            description="Run merge conflict workflow on a source fork",
            additional_arguments={
                "source": {
                    "type": str,
                    "help": "URL of the source fork containing PRs to merge",
                    "required": True,
                },
                "branch": {
                    "type": str,
                    "help": "Branch on source fork containing PRs to merge",
                    "required": True,
                },
            },
            prompts=PROMPTS,
        )
        self.workflow = None

    def _setup(
        self,
        github_token_env_var: str = "GITHUB_TOKEN",
        github_username_env_var: str = "GITHUB_USERNAME",
        required_env_vars: List[str] = None,
        **kwargs,
    ):
        """Set up merge conflict workflow context.

        Args:
            github_token_env_var: Name of env var containing GitHub token
            github_username_env_var: Name of env var containing GitHub username
            required_env_vars: Additional required environment variables
        """
        # Combine GitHub env vars with any additional required vars
        env_vars = [github_token_env_var, github_username_env_var]
        if required_env_vars:
            env_vars.extend(required_env_vars)

        super()._setup(required_env_vars=env_vars, prompts=PROMPTS)

        repo_url = self.args.source
        source_owner, source_repo = self._parse_github_url(repo_url)

        # Get upstream repo info using original source fork
        gh = Github(os.getenv(github_token_env_var))
        source_fork = gh.get_repo(f"{source_owner}/{source_repo}")
        if not source_fork.fork:
            raise Exception("Source repository is not a fork")

        # Parse task_id and round_number from branch name
        # Format: task-{task_id}-round-{round_number}
        branch_parts = self.args.branch.split("-")
        if (
            len(branch_parts) != 4
            or branch_parts[0] != "task"
            or branch_parts[2] != "round"
        ):
            raise ValueError(
                f"Invalid branch format: {self.args.branch}. Expected: task-<task_id>-round-<round_number>"
            )

        task_id = branch_parts[1]
        round_number = int(branch_parts[3])

        # Add task ID, round number, and signatures to context
        self._add_signature_context(additional_payload={"action": "merge"})

        # Create workflow instance
        self.workflow = MergeConflictWorkflow(
            client=self.client,
            prompts=self.prompts,
            source_fork_url=repo_url,
            source_branch=self.args.branch,
            task_id=task_id,
            round_number=round_number,
            staking_key=self.context["staking_key"],
            pub_key=self.context["pub_key"],
            staking_signature=self.context["staking_signature"],
            public_signature=self.context["public_signature"],
            github_token=github_token_env_var,
            github_username=github_username_env_var,
        )

    def _run(self, **kwargs):
        """Run the merge conflict workflow."""
        result = self.workflow.run()

        if result:
            print(f"Successfully created consolidated PR: {result}")
        else:
            raise Exception("No PRs were processed or PR creation failed")
