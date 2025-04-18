"""Task decomposition workflow implementation."""

import os
from github import Github
from prometheus_swarm.workflows.base import Workflow
from prometheus_swarm.utils.logging import log_section, log_key_value, log_error
from src.workflows.repoSummarizerAudit import phases
from prometheus_swarm.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repository,
    cleanup_repository,
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


class repoSummarizerAuditWorkflow(Workflow):
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
        pr_number = int(parts[-1])  # Convert to integer
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
        self.context["repo_full_name"] = f"{repo_owner}/{repo_name}"

    def setup(self):
        """Set up repository and workspace."""
        # Check required environment variables and validate GitHub auth
        check_required_env_vars(["GITHUB_TOKEN", "GITHUB_USERNAME"])
        validate_github_auth(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USERNAME"))
        self.context["repo_url"] = f"https://github.com/{self.context['repo_owner']}/{self.context['repo_name']}"
        # Set up repository directory
        setup_result = setup_repository(self.context["repo_url"], github_token=os.getenv("GITHUB_TOKEN"), github_username=os.getenv("GITHUB_USERNAME"))
        if not setup_result["success"]:
            raise Exception(f"Failed to set up repository: {setup_result['message']}")
            
        self.context["repo_path"] = setup_result["data"]["clone_path"]
        self.original_dir = setup_result["data"]["original_dir"]
        self.context["fork_url"] = setup_result["data"]["fork_url"]
        self.context["fork_owner"] = setup_result["data"]["fork_owner"]
        self.context["fork_name"] = setup_result["data"]["fork_name"]
        self.context["github_token"] = os.getenv("GITHUB_TOKEN")
        # Enter repo directory
        os.chdir(self.context["repo_path"])
        gh = Github(self.context["github_token"])
        repo = gh.get_repo(
            f"{self.context['repo_owner']}/{self.context['repo_name']}"
        )
        pr = repo.get_pull(self.context["pr_number"])
        self.context["pr"] = pr
        # Add remote for PR's repository and fetch the branch
        os.system(
            f"git remote add pr_source https://github.com/{pr.head.repo.full_name}"
        )
        os.system(f"git fetch pr_source {pr.head.ref}")
        os.system("git checkout FETCH_HEAD")

        # Get current files for context
        self.context["current_files"] = get_current_files()

    def cleanup(self):
        """Cleanup workspace."""
        # Make sure we're not in the repo directory before cleaning up
        if os.getcwd() == self.context.get("repo_path", ""):
            os.chdir(self.original_dir)

        # Clean up the repository directory
        cleanup_repository(self.original_dir, self.context.get("repo_path", ""))
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
            if not check_readme_file_result or not check_readme_file_result.get(
                "success"
            ):
                log_error(
                    Exception(check_readme_file_result.get("error", "No result")),
                    "Readme file check failed",
                )
                return {
                    "success": False,
                    "message": "Readme file check failed",
                    "data": {
                        "recommendation": False,
                    },
                }
            log_section("Readme file check completed")
            print(check_readme_file_result)
            recommendation = check_readme_file_result["data"]["recommendation"]
            log_key_value(
                "Readme file check completed", f"Recommendation: {recommendation}"
            )
            # Star the repository
            return {
                "success": True,
                "message": "Readme file check completed",
                "data": {
                    "recommendation": recommendation == "APPROVE",
                },
            }
        except Exception as e:
            log_error(e, "Readme file check workflow failed")
            print(e)
            return {
                "success": False,
                "message": f"Readme file check workflow failed: {str(e)}",
                "data": {
                    "recommendation": False,
                },
            }
