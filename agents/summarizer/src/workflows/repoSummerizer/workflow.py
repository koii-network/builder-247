"""Task decomposition workflow implementation."""

import os
from github import Github
from src.workflows.base import Workflow
from src.tools.github_operations.implementations import fork_repository, create_pull_request
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


class RepoSummerizerWorkflow(Workflow):
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
        generate_readme_file_result = self.generate_readme_file()
        
        # Create pull request with detailed parameters
        create_pull_request_result = create_pull_request(
            repo_full_name=f"{self.context['repo_owner']}/{self.context['repo_name']}", 
            title="Update README.md",
            head=self.context["base_branch"],  # or a specific branch name
            description="Automated update of README.md file with repository summary",
            tests=["README.md file has been updated", "Content is properly formatted"],
            todo="Review and merge the README changes",
            acceptance_criteria="README.md contains accurate repository summary",
            base=self.context["base_branch"]
        )
        log_key_value("Create pull request result", create_pull_request_result)
        
        return create_pull_request_result
    def generate_readme_file(self):
        """Execute the issue generation workflow."""
        try:
            self.setup()
            # ==================== Generate issues ====================
            generate_readme_file_phase = phases.ReadmeGenerationPhase(workflow=self)
            generate_readme_file_result = generate_readme_file_phase.execute()
            # Check Issue Generation Result
            if not generate_readme_file_result or not generate_readme_file_result.get("success"):
                log_error(
                    Exception(generate_readme_file_result.get("error", "No result")),
                    "Readme file generation failed",
                )
                return None
            # Star the repository
            return generate_readme_file_result
        except Exception as e:
            log_error(e, "Readme file generation workflow failed")
            print(e)
            return {
                "success": False,
                "message": f"Readme file generation workflow failed: {str(e)}",
                "data": None,
            }
    