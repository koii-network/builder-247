"""Task workflow execution."""

import os
from github import Github, GithubException
from src.workflows.base import WorkflowExecution
from src.workflows.task.workflow import TaskWorkflow
from src.workflows.task.prompts import PROMPTS
from src.workflows.utils import create_remote_branch
from src.utils.logging import log_key_value
from typing import List


class TaskExecution(WorkflowExecution):
    def __init__(self):
        super().__init__(
            description="Run task workflow on GitHub repository",
            additional_arguments={
                "repo": {
                    "type": str,
                    "required": True,
                    "help": "GitHub repository URL to create PRs to (e.g., https://github.com/owner/repo)",
                },
                "todo": {
                    "type": str,
                    "required": True,
                    "help": "Todo task description",
                },
                "acceptance-criteria": {
                    "type": str,
                    "required": True,
                    "help": "Semicolon-separated list of acceptance criteria",
                },
            },
            prompts=PROMPTS,
        )

    def _setup(
        self,
        leader_token_env_var: str = "LEADER_GITHUB_TOKEN",
        leader_username_env_var: str = "LEADER_GITHUB_USERNAME",
        worker_token_env_var: str = "WORKER_GITHUB_TOKEN",
        worker_username_env_var: str = "WORKER_GITHUB_USERNAME",
        additional_env_vars: List[str] = None,
    ):
        """Set up task workflow context.

        Args:
            leader_token_env_var: Name of env var containing leader's GitHub token
            leader_username_env_var: Name of env var containing leader's GitHub username
            worker_token_env_var: Name of env var containing worker's GitHub token
            worker_username_env_var: Name of env var containing worker's GitHub username
            additional_env_vars: Additional required environment variables
        """
        # Combine GitHub env vars with any additional required vars
        required_env_vars = [
            leader_token_env_var,
            leader_username_env_var,
            worker_token_env_var,
            worker_username_env_var,
        ]
        if additional_env_vars:
            required_env_vars.extend(additional_env_vars)

        super()._setup(required_env_vars=required_env_vars)

        # Parse acceptance criteria into list
        acceptance_criteria = [
            criterion.strip()
            for criterion in self.args.acceptance_criteria.split(";")
            if criterion.strip()
        ]

        # Add task ID, round number, and signatures to context
        self._add_signature_context(
            payload={
                "todo": self.args.todo,
                "acceptance_criteria": acceptance_criteria,
                "action": "task",
            }
        )

        # Parse source repo URL
        source_owner, source_repo = self._parse_github_url(self.args.repo)

        # Set up leader's fork
        leader_gh = Github(os.getenv(leader_token_env_var))
        source = leader_gh.get_repo(f"{source_owner}/{source_repo}")
        leader_user = leader_gh.get_user()

        try:
            leader_fork = leader_gh.get_repo(f"{leader_user.login}/{source_repo}")
            log_key_value("Using existing leader fork", leader_fork.html_url)
        except GithubException:
            leader_fork = leader_user.create_fork(source)
            log_key_value("Created leader fork", leader_fork.html_url)

        # Create unique base branch on leader's fork
        base_branch = (
            f"task-{self.context['task_id']}-round-{self.context['round_number']}"
        )
        create_result = create_remote_branch(
            repo_owner=leader_user.login,
            repo_name=source_repo,
            branch_name=base_branch,
            github_token=os.getenv(leader_token_env_var),
        )
        if not create_result["success"]:
            raise Exception(
                f"Failed to create base branch: {create_result.get('error', 'Unknown error')}"
            )

        # Create workflow instance
        self.workflow = TaskWorkflow(
            client=self.client,
            prompts=self.prompts,
            repo_owner=leader_user.login,
            repo_name=source_repo,
            todo=self.args.todo,
            acceptance_criteria=acceptance_criteria,
            staking_key=self.context["staking_key"],
            pub_key=self.context["pub_key"],
            staking_signature=self.context["staking_signature"],
            public_signature=self.context["public_signature"],
            round_number=self.context["round_number"],
            task_id=self.context["task_id"],
            base_branch=base_branch,
            github_token=os.getenv(worker_token_env_var),
            github_username=os.getenv(worker_username_env_var),
        )

    def _run(self):
        """Run the task workflow."""
        result = self.workflow.run()

        if result is None:
            raise Exception("Task workflow failed")

        return result
