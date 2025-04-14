"""Task decomposition workflow implementation."""

import os
from github import Github
from src.workflows.base import Workflow
from src.tools.github_operations.implementations import fork_repository
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.audit import phases
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repo_directory,
    setup_git_user_config,
    cleanup_repo_directory,
    get_current_files,
)
# from src.workflows.todocreator.utils import TaskModel, IssueModel, insert_issue_to_mongodb

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


class AuditWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        issuesAndTasks,
        issueSpec,
        repo_owner,
        repo_name,
    ):
        # Extract owner and repo name from URL
        # URL format: https://github.com/owner/repo
        repo_url = f"https://github.com/{repo_owner}/{repo_name}"

        
        super().__init__(
            client=client,
            prompts=prompts,
            repo_url=repo_url,
            repo_owner=repo_owner,
            repo_name=repo_name,
            issuesAndTasks=issuesAndTasks,
            issueSpec=issueSpec,
        )
        self.issuesAndTasks = issuesAndTasks
        self.issueSpec = issueSpec

    def setup(self):
        """Set up repository and workspace."""
        # Set context values first

        
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

        # Set up repository directory
        repo_path, original_dir = setup_repo_directory()
        self.context["repo_path"] = repo_path
        self.original_dir = original_dir

        # Fork and clone repository
        log_section("FORKING AND CLONING REPOSITORY")
        fork_result = fork_repository(
            f"{self.context['repo_owner']}/{self.context['repo_name']}",
            self.context["repo_path"],
        )
        if not fork_result["success"]:
            error = fork_result.get("error", "Unknown error")
            log_error(Exception(error), "Fork failed")
            raise Exception(error)

        # Enter repo directory
        os.chdir(self.context["repo_path"])

        # Configure Git user info
        setup_git_user_config(self.context["repo_path"])

        # Get current files for context
        self.context["current_files"] = get_current_files()

        # Add feature spec to context
        # self.context["feature_spec"] = self.feature_spec
        self.context["issue_spec"] = self.issueSpec

    def cleanup(self):
        """Cleanup workspace."""
        # Make sure we're not in the repo directory before cleaning up
        if os.getcwd() == self.context.get("repo_path", ""):
            os.chdir(self.original_dir)

        # Clean up the repository directory
        cleanup_repo_directory(self.original_dir, self.context.get("repo_path", ""))
        # Clean up the MongoDB
    def run(self):
        validate_tasks_result = self.validate_tasks()

        
        return {
            "success": True,
            "result": validate_tasks_result["data"]["result"],
          
        }
    def validate_tasks(self):
        """Execute the issue generation workflow."""

        issues = []
        try:
            self.setup()
            # ==================== Generate issues ====================
            Task_Validation_Phase = phases.TaskValidationPhase(workflow=self)
            Task_Validation_Result = Task_Validation_Phase.execute()
            # Check Task Validation Result
            if not Task_Validation_Result or not Task_Validation_Result.get("success"):
                log_error(
                    Exception(Task_Validation_Result.get("error", "No result")),
                    "Task validation failed",
                )
            return Task_Validation_Result
        except Exception as e:
            log_error(e, "Issue generation workflow failed")
            print(e)
            return {
                "success": False,
                "message": f"Issue generation workflow failed: {str(e)}",
                "data": {
                    "issues": issues
                }
            }
