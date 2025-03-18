"""Task decomposition workflow implementation."""

import os
from github import Github
from src.workflows.base import Workflow
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.todocreator import phases
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_git_user_config,
    get_current_files,
    repository_context,
)


class Task:
    def __init__(self, title: str, description: str, acceptance_criteria: list[str]):
        self.title = title
        self.description = description
        self.acceptance_criteria = acceptance_criteria

    def to_dict(self) -> dict:
        """Convert task to dictionary format."""
        return {
            "title": self.title,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        return cls(
            title=data["title"],
            description=data["description"],
            acceptance_criteria=data["acceptance_criteria"],
        )


class TodoCreatorWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        repo_url,
        feature_spec,
        output_csv_path="tasks.csv",
    ):
        # Extract owner and repo name from URL
        # URL format: https://github.com/owner/repo
        parts = repo_url.strip("/").split("/")
        repo_owner = parts[-2]
        repo_name = parts[-1]

        super().__init__(
            client=client,
            prompts=prompts,
            repo_url=repo_url,
            repo_owner=repo_owner,
            repo_name=repo_name,
            output_csv_path=output_csv_path,
        )
        self.feature_spec = feature_spec
        self.tasks: list[Task] = []

    def setup(self):
        """Set up repository and workspace."""
        check_required_env_vars(["GITHUB_TOKEN", "GITHUB_USERNAME"])
        validate_github_auth(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USERNAME"))

        # Get the default branch from GitHub
        try:
            gh = Github(os.getenv("GITHUB_TOKEN"))
            repo = gh.get_repo(
                f"{self.context['repo_owner']}/{self.context['repo_name']}"
            )
            self.context["base_branch"] = repo.default_branch
            log_key_value("Default branch", self.context["base_branch"])
        except Exception as e:
            log_error(e, "Failed to get default branch, using 'main'")
            self.context["base_branch"] = "main"

        # Set up repository
        log_section("SETTING UP REPOSITORY")
        repo_url = f"https://github.com/{self.context['repo_owner']}/{self.context['repo_name']}"
        with repository_context(
            repo_url, github_token=os.getenv("GITHUB_TOKEN")
        ) as setup_result:
            # Update context with setup results
            self.context.update(
                {
                    "repo_path": setup_result["data"]["clone_path"],
                    "original_dir": setup_result["data"]["original_dir"],
                }
            )

            # Enter repo directory
            os.chdir(self.context["repo_path"])

            # Configure Git user info
            setup_git_user_config(self.context["repo_path"])

            # Get current files for context
            self.context["current_files"] = get_current_files()

            # Add feature spec to context
            self.context["feature_spec"] = self.feature_spec

    def cleanup(self):
        """Cleanup is now handled by repository_context."""
        pass

    def run(self):
        """Execute the task decomposition workflow."""
        try:
            self.setup()

            # Store the output filename in the context for the agent to use
            # Make sure it has a .csv extension
            output_filename = self.context.get("output_csv_path", "tasks.csv")
            if not output_filename.endswith(".csv"):
                output_filename = f"{os.path.splitext(output_filename)[0]}.csv"
                self.context["output_csv_path"] = output_filename

            # Log the output filename that will be used
            log_key_value("Output CSV file", output_filename)

            # Decompose feature into tasks and generate CSV
            decompose_phase = phases.TaskDecompositionPhase(workflow=self)
            decomposition_result = decompose_phase.execute()

            if not decomposition_result or not decomposition_result.get("success"):
                log_error(
                    Exception(decomposition_result.get("error", "No result")),
                    "Task decomposition failed",
                )
                return None

            # Get the tasks and file path from the result
            tasks_data = decomposition_result["data"].get("tasks", [])
            output_csv = decomposition_result["data"].get("file_path")
            task_count = decomposition_result["data"].get("task_count", 0)

            if not tasks_data:
                log_error(
                    Exception("No tasks generated"),
                    "Task decomposition failed",
                )
                return None

            # Convert raw tasks to Task objects
            self.tasks = [Task.from_dict(task) for task in tasks_data]

            log_key_value("CSV file created at", output_csv)
            log_key_value("Tasks created", task_count)

            # Return the final result
            return {
                "success": True,
                "message": f"Created {task_count} tasks for the feature",
                "data": {
                    "tasks": [task.to_dict() for task in self.tasks],
                    "output_csv": output_csv,
                    "task_count": task_count,
                },
            }

        except Exception as e:
            log_error(e, "Task decomposition workflow failed")
            return {
                "success": False,
                "message": f"Task decomposition workflow failed: {str(e)}",
                "data": None,
            }
        finally:
            self.cleanup()
