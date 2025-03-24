"""Task decomposition workflow implementation."""

import os
from github import Github
from src.workflows.base import Workflow
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.repoSummerizerAudit import phases
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repo_directory,
    cleanup_repo_directory,
    get_current_files,
)
from git import Repo

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


class RepoSummerizerAuditWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        pr_url,
    ):
        # Extract owner and repo name from URL
        # URL format: https://github.com/owner/repo
        parts = pr_url.strip("/").split("/")
        repo_owner = parts[-4]
        repo_name = parts[-3]
        pr_number = parts[-1]
        super().__init__(
            client=client,
            prompts=prompts,
            repo_owner=repo_owner,
            repo_name=repo_name,
            pr_number=pr_number,
        )
        self.context["pr_number"] = pr_number
        self.context["pr_url"] = pr_url
        self.context["repo_owner"] = repo_owner
        self.context["repo_name"] = repo_name


    def setup(self):
        """Set up repository and workspace."""
        # Check required environment variables and validate GitHub auth
        check_required_env_vars(["GITHUB_TOKEN", "GITHUB_USERNAME"])
        validate_github_auth(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USERNAME"))

        # Set up repository directory
        repo_path, original_dir = setup_repo_directory()
        self.context["repo_path"] = repo_path
        self.context["original_dir"] = original_dir

        # Clone repository
        log_section("CLONING REPOSITORY")
        gh = Github(os.environ["GITHUB_TOKEN"])
        log_key_value("Getting repository", f"{self.context['repo_owner']}/{self.context['repo_name']}")
        repo = gh.get_repo(f"{self.context['repo_owner']}/{self.context['repo_name']}")

        log_key_value("Cloning repository to", self.context["repo_path"])
        git_repo = Repo.clone_from(repo.clone_url, self.context["repo_path"])

        # Fetch PR
        log_key_value("Fetching PR", f"#{self.context['pr_number']}")
        git_repo.remote().fetch(
            f"pull/{self.context['pr_number']}/head:pr_{self.context['pr_number']}"
        )

        # Checkout PR branch
        log_key_value("Checking out PR branch", f"pr_{self.context['pr_number']}")
        git_repo.git.checkout(f"pr_{self.context['pr_number']}")

        # Enter repo directory
        os.chdir(self.context["repo_path"])
        self.context["current_files"] = get_current_files()


    def cleanup(self):
        """Cleanup workspace."""
        # Make sure we're not in the repo directory before cleaning up
        if os.getcwd() == self.context.get("repo_path", ""):
            os.chdir(self.original_dir)

        # Clean up the repository directory
        cleanup_repo_directory(self.original_dir, self.context.get("repo_path", ""))
        # Clean up the MongoDB
    def run(self):
        check_readme_file_result = self.check_readme_file()
        
        return check_readme_file_result
    def check_readme_file(self):
        """Execute the issue generation workflow."""
        try:
            self.setup()
            # ==================== Generate issues ====================
            check_readme_file_phase = phases.CheckReadmeFilePhase(workflow=self)
            check_readme_file_result = check_readme_file_phase.execute()
            # Check Issue Generation Result
            if not check_readme_file_result or not check_readme_file_result.get("success"):
                log_error(
                    Exception(check_readme_file_result.get("error", "No result")),
                    "Readme file check failed",
                )
                return None
            log_section("Readme file check completed")
            print(check_readme_file_result)
            recommendation = check_readme_file_result["data"]["recommendation"]
            log_key_value("Readme file check completed", f"Recommendation: {recommendation}")
            # Star the repository
            return check_readme_file_result
        except Exception as e:
            log_error(e, "Readme file check workflow failed")
            print(e)
            return {
                "success": False,
                "message": f"Readme file check workflow failed: {str(e)}",
                "data": None,
            }
    