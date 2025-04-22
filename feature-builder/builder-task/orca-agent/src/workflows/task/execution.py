"""Task workflow execution."""

import os
import csv
from pathlib import Path
from github import Github, GithubException
from prometheus_swarm.workflows.base import WorkflowExecution
from prometheus_swarm.workflows.utils import create_remote_branch
from prometheus_swarm.utils.logging import log_key_value, log_section
from src.workflows.task.workflow import TaskWorkflow
from src.workflows.task.prompts import PROMPTS

from typing import List, Optional, Dict


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
                    "default": "test_todos.csv",
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
        self.todo_pr_urls: Dict[str, str] = {}  # Map of todo UUID to PR URL

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

        print("Loading todos from", self.todos_file)

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

    def _get_dependency_pr_urls(
        self, task_uuid: str, dependency_uuids: List[str]
    ) -> List[str]:
        """Get PR URLs for a task's dependencies.

        Args:
            task_uuid: UUID of the current task
            dependency_uuids: List of dependency UUIDs

        Returns:
            List of PR URLs for the dependencies
        """
        pr_urls = []
        for dep_uuid in dependency_uuids:
            if dep_uuid not in self.todo_pr_urls:
                raise Exception(
                    f"Dependency {dep_uuid} for task {task_uuid} has not been completed yet"
                )
            pr_urls.append(self.todo_pr_urls[dep_uuid])
        return pr_urls

    def _run(self, **kwargs):
        """Run the task workflow."""
        try:
            # First pass: read all todos to understand dependencies
            todos = []
            with self.todos_file.open("r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        todo, acceptance_criteria_str = row[0], row[1]
                        # Parse acceptance criteria string into list
                        acceptance_criteria = [
                            criterion.strip()
                            for criterion in acceptance_criteria_str.split(";")
                            if criterion.strip()
                        ]

                        # Parse task UUID and dependencies if present
                        task_uuid = None
                        dependency_uuids = []
                        if len(row) >= 3 and row[2]:
                            task_uuid = row[2]
                        if len(row) >= 4 and row[3]:
                            # Split on comma and strip whitespace
                            dependency_uuids = [
                                uuid.strip()
                                for uuid in row[3].split(",")
                                if uuid.strip()
                            ]

                        todos.append(
                            {
                                "todo": todo,
                                "acceptance_criteria": acceptance_criteria,
                                "task_uuid": task_uuid,
                                "dependency_uuids": dependency_uuids,
                            }
                        )

            # Second pass: process todos in order
            for i, todo_data in enumerate(todos):
                log_section(f"PROCESSING TODO {i}")

                # Get PR URLs for dependencies
                dependency_pr_urls = []
                if todo_data["dependency_uuids"]:
                    try:
                        dependency_pr_urls = self._get_dependency_pr_urls(
                            todo_data["task_uuid"], todo_data["dependency_uuids"]
                        )
                    except Exception as e:
                        log_key_value("Error", str(e))
                        continue

                # Add task ID, round number, and signatures to context
                self._add_signature_context(
                    additional_payload={
                        "todo": todo_data["todo"],
                        "acceptance_criteria": todo_data["acceptance_criteria"],
                        "action": "task",
                    }
                )

                # Create workflow instance
                self.workflow = TaskWorkflow(
                    client=self.client,
                    prompts=self.prompts,
                    repo_owner=self.leader_user.login,
                    repo_name=self.source_repo,
                    todo=todo_data["todo"].strip(),
                    acceptance_criteria=todo_data["acceptance_criteria"],
                    staking_key=self.context["staking_key"],
                    pub_key=self.context["pub_key"],
                    staking_signature=self.context["staking_signature"],
                    public_signature=self.context["public_signature"],
                    round_number=self.context["round_number"],
                    task_id=self.context["task_id"],
                    base_branch=self.base_branch,
                    github_token="WORKER_GITHUB_TOKEN",  # Pass env var name instead of value
                    github_username="WORKER_GITHUB_USERNAME",  # Pass env var name instead of value
                    dependency_pr_urls=dependency_pr_urls,
                )

                result = self.workflow.run()
                if result is None:
                    raise Exception(f"Task workflow failed for todo {i}")

                # Store the PR URL for this task
                if todo_data["task_uuid"]:
                    self.todo_pr_urls[todo_data["task_uuid"]] = result

            return True

        except Exception:
            raise
