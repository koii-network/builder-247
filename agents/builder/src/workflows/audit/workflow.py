"""Audit workflow implementation."""

import os
from git import Repo
from github import Github

from src.workflows.base import Workflow
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repo_directory,
    cleanup_repo_directory,
    get_current_files,
)
from src.workflows.audit.phases import AuditPhase


class AuditWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        pr_url,
        staking_key,
        pub_key,
        staking_signature,
        public_signature,
    ):
        repo_owner, repo_name, pr_number = self._parse_github_pr_url(pr_url)
        super().__init__(
            client=client,
            prompts=prompts,
            repo_owner=repo_owner,
            repo_name=repo_name,
            pr_number=pr_number,
            staking_key=staking_key,
            pub_key=pub_key,
            staking_signature=staking_signature,
            public_signature=public_signature,
        )

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

    def _parse_github_pr_url(self, pr_url: str) -> tuple[str, str, int]:
        """
        Parse a GitHub pull request URL to extract owner, repo name, and PR number.

        Args:
            pr_url: GitHub pull request URL (e.g., 'https://github.com/owner/repo/pull/123')

        Returns:
            Tuple of (owner, repo_name, pr_number)

        Raises:
            ValueError: If the URL format is invalid
        """
        try:
            # Remove trailing slash if present
            pr_url = pr_url.rstrip("/")

            # Handle both HTTPS and SSH formats
            if pr_url.startswith("https://github.com/"):
                path = pr_url.replace("https://github.com/", "")
            elif pr_url.startswith("git@github.com:"):
                path = pr_url.replace("git@github.com:", "")
            else:
                raise ValueError(
                    "URL must start with 'https://github.com/' or 'git@github.com:'"
                )

            # Split path into components
            parts = path.split("/")
            if len(parts) != 4 or parts[2] != "pull" or not parts[3].isdigit():
                raise ValueError(
                    "Invalid PR URL format. Expected format: owner/repo/pull/number"
                )

            return parts[0], parts[1], int(parts[3])
        except Exception as e:
            raise ValueError(f"Failed to parse GitHub PR URL: {str(e)}")

    def cleanup(self):
        """Cleanup workspace."""
        cleanup_repo_directory(
            self.context["original_dir"], self.context.get("repo_path", "")
        )

    def run(self):
        """Execute the audit workflow."""
        try:
            self.setup()

            # Get current files
            self.context["files_directory"] = get_current_files()

            # Define review phase
            review_phase = AuditPhase(workflow=self)

            review_result = review_phase.execute()

            if not review_result:
                return None

            recommendation = review_result["data"]["recommendation"]
            log_key_value("Review completed", f"Recommendation: {recommendation}")

        except Exception as e:
            log_error(e, "Error in audit workflow")
            raise

        finally:
            self.cleanup()
