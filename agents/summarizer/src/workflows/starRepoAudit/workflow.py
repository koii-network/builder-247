"""Task decomposition workflow implementation."""

import os
from github import Github
from src.workflows.base import Workflow
from src.tools.github_operations.implementations import fork_repository, star_repository
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.repoSummerizer import phases
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repo_directory,
    setup_git_user_config,
    cleanup_repo_directory,
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


class StarRepoAuditWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        repo_url,
        github_username,
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
            github_username=github_username,
            
        )
        self.context["repo_owner"] = repo_owner
        self.context["repo_name"] = repo_name
        self.context["github_username"] = github_username


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

    def cleanup(self):
        """Cleanup workspace."""
        # Make sure we're not in the repo directory before cleaning up
        if os.getcwd() == self.context.get("repo_path", ""):
            os.chdir(self.original_dir)

        # Clean up the repository directory
        cleanup_repo_directory(self.original_dir, self.context.get("repo_path", ""))
        # Clean up the MongoDB
    def run(self):
        star_repo_result = self.check_star_repo()
        if not star_repo_result:
            log_error(Exception("Repository is not starred"), "Repository is not starred")
            return False
        return star_repo_result
    def check_star_repo(self):
        """Check if the repository is starred."""
        try:
            starred_repos = get_user_starred_repos(self.context["github_username"])
            if not starred_repos or not starred_repos.get("success"):
                log_error(
                    Exception(starred_repos.get("error", "No result")),
                    "Failed to get starred repositories",
                )
                return False
            # check if the repository is in the starred_repos
            if self.context["repo_name"] in [repo["full_name"] for repo in starred_repos["data"]["starred_repos"]]:
                return True
            else:
                return False
        except Exception as e:
            log_error(e, "Failed to check if repository is starred")
            return False
