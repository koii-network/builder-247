"""Task decomposition workflow implementation."""

import os
from github import Github
from prometheus_swarm.workflows.base import Workflow
from prometheus_swarm.tools.github_operations.implementations import star_repository
from prometheus_swarm.utils.logging import log_section, log_key_value, log_error
from src.workflows.repoSummarizer import phases
from prometheus_swarm.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
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


class StarRepoWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        repo_url,
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
        )
        self.context["repo_owner"] = repo_owner
        self.context["repo_name"] = repo_name
        self.context["github_token"] = os.getenv("GITHUB_TOKEN")

    def setup(self):
        """Set up repository and workspace."""
        check_required_env_vars(["GITHUB_TOKEN", "GITHUB_USERNAME"])
        validate_github_auth(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USERNAME"))

        # # Get the default branch from GitHub
        # try:
        #     gh = Github(os.getenv("GITHUB_TOKEN"))
        #     repo = gh.get_repo(
        #         f"{self.context['repo_owner']}/{self.context['repo_name']}"
        #     )
        #     self.context["base_branch"] = repo.default_branch
        #     log_key_value("Default branch", self.context["base_branch"])
        # except Exception as e:
        #     log_error(e, "Failed to get default branch, using 'main'")
        #     self.context["base_branch"] = "main"

        # Set up repository directory
        # repo_path, original_dir = setup_repo_directory()
        # self.context["repo_path"] = repo_path
        # self.original_dir = original_dir

        # # Fork and clone repository
        # log_section("FORKING AND CLONING REPOSITORY")
        # fork_result = fork_repository(
        #     f"{self.context['repo_owner']}/{self.context['repo_name']}",
        #     self.context["repo_path"],
        # )
        # if not fork_result["success"]:
        #     error = fork_result.get("error", "Unknown error")
        #     log_error(Exception(error), "Fork failed")
        #     raise Exception(error)

        # # Enter repo directory
        # os.chdir(self.context["repo_path"])

        # # Configure Git user info
        # setup_git_user_config(self.context["repo_path"])

        # Get current files for context

    def cleanup(self):
        """Cleanup workspace."""
            # cleanup_repository(self.original_dir, self.context.get("repo_path", ""))
        # Make sure we're not in the repo directory before cleaning up
        # if os.getcwd() == self.context.get("repo_path", ""):
        #     os.chdir(self.original_dir)

        # # Clean up the repository directory
        # cleanup_repo_directory(self.original_dir, self.context.get("repo_path", ""))
        # Clean up the MongoDB

    def run(self):
        star_repo_result = self.start_star_repo()
        return star_repo_result

    def start_star_repo(self):
        """Execute the issue generation workflow."""
        try:
            self.setup()
            # ==================== Generate issues ====================
            star_repo_result = star_repository(
                self.context["repo_owner"], self.context["repo_name"], self.context["github_token"]
            )
            if not star_repo_result or not star_repo_result.get("success"):
                log_error(
                    Exception(star_repo_result.get("error", "No result")),
                    "Repository star failed",
                )
                return None
            return star_repo_result
        except Exception as e:
            log_error(e, "Readme file generation workflow failed")
            print(e)
            return {
                "success": False,
                "message": f"Readme file generation workflow failed: {str(e)}",
                "data": None,
            }
