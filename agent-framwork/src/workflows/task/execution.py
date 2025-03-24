"""Task workflow execution."""

import os
import csv
from pathlib import Path
from github import Github, GithubException
from src.workflows.base import WorkflowExecution
from src.workflows.task.workflow import TaskWorkflow
from src.workflows.task.prompts import PROMPTS
from src.workflows.utils import create_remote_branch
from src.utils.logging import log_key_value, log_section
from typing import List, Optional


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
                "input": {
                    "type": str,
                    "help": "Path to CSV file containing todos and acceptance criteria",
                    "default": "test_todos_small.csv",
                },
            },
            prompts=PROMPTS,
        )
        self.leader_token = None
        self.leader_user = None
        self.source_owner = None
        self.source_repo = None
        self.todos_file = None
        self.base_branch = None

    def _setup(
        self,
        required_env_vars: Optional[List[str]] = None,
        leader_token_env_var: str = "LEADER_GITHUB_TOKEN",
        leader_username_env_var: str = "LEADER_GITHUB_USERNAME",
        worker_token_env_var: str = "WORKER_GITHUB_TOKEN",
        worker_username_env_var: str = "WORKER_GITHUB_USERNAME",
        **kwargs,
    ):
        """Set up task workflow context.

        Args:
            required_env_vars: List of required environment variables
            leader_token_env_var: Name of env var containing leader's GitHub token
            leader_username_env_var: Name of env var containing leader's GitHub username
            worker_token_env_var: Name of env var containing worker's GitHub token
            worker_username_env_var: Name of env var containing worker's GitHub username
        """
        # Combine GitHub env vars with any additional required vars
        env_vars = [
            leader_token_env_var,
            leader_username_env_var,
            worker_token_env_var,
            worker_username_env_var,
            "DATA_DIR",
        ]
        if required_env_vars:
            env_vars.extend(required_env_vars)

        super()._setup(required_env_vars=env_vars)

        # Get data directory from environment
        data_dir = Path(os.environ["DATA_DIR"])
        self.todos_file = data_dir / self.args.input

        if not self.todos_file.exists():
            raise Exception(f"Todos file not found at {self.todos_file}")

        # Parse source repo URL
        self.source_owner, self.source_repo = self._parse_github_url(self.args.repo)

        # Set up leader's fork
        self.leader_token = os.getenv(leader_token_env_var)
        leader_gh = Github(self.leader_token)
        source = leader_gh.get_repo(f"{self.source_owner}/{self.source_repo}")
        self.leader_user = leader_gh.get_user()

        try:
            leader_fork = leader_gh.get_repo(
                f"{self.leader_user.login}/{self.source_repo}"
            )
            log_key_value("Using existing leader fork", leader_fork.html_url)
        except GithubException:
            leader_fork = self.leader_user.create_fork(source)
            log_key_value("Created leader fork", leader_fork.html_url)

        # Create base branch that all PRs will target
        self.base_branch = f"task-{self.args.task_id}-round-{self.args.round_number}"
        create_result = create_remote_branch(
            repo_owner=self.leader_user.login,
            repo_name=self.source_repo,
            branch_name=self.base_branch,
            github_token=self.leader_token,
        )
        if not create_result["success"]:
            raise Exception(
                f"Failed to create base branch: {create_result.get('error', 'Unknown error')}"
            )
        log_key_value("Base branch", self.base_branch)

    def _run(self, **kwargs):
        """Run the task workflow."""
        try:
            with self.todos_file.open("r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for i, row in enumerate(reader):
                    if len(row) >= 2:
                        todo, acceptance_criteria_str = row[0], row[1]
                        # Parse acceptance criteria string into list
                        acceptance_criteria = [
                            criterion.strip()
                            for criterion in acceptance_criteria_str.split(";")
                            if criterion.strip()
                        ]

                        log_section(f"PROCESSING TODO {i}")

                        # Add task ID, round number, and signatures to context
                        self._add_signature_context(
                            additional_payload={
                                "todo": todo,
                                "acceptance_criteria": acceptance_criteria,
                                "action": "task",
                            }
                        )

                        # Create workflow instance
                        self.workflow = TaskWorkflow(
                            client=self.client,
                            prompts=self.prompts,
                            repo_owner=self.leader_user.login,
                            repo_name=self.source_repo,
                            todo=todo.strip(),
                            acceptance_criteria=acceptance_criteria,
                            staking_key=self.context["staking_key"],
                            pub_key=self.context["pub_key"],
                            staking_signature=self.context["staking_signature"],
                            public_signature=self.context["public_signature"],
                            round_number=self.context["round_number"],
                            task_id=self.context["task_id"],
                            base_branch=self.base_branch,
                            github_token="WORKER_GITHUB_TOKEN",  # Pass env var name instead of value
                            github_username="WORKER_GITHUB_USERNAME",  # Pass env var name instead of value
                        )

                        result = self.workflow.run()
                        if result is None:
                            raise Exception(f"Task workflow failed for todo {i}")
                    else:
                        log_key_value("Skipping invalid row", row)

            return True

        except Exception:
            raise
