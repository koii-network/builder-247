"""Audit workflow implementation."""

import os
from github import Github
from src.workflows.base import Workflow
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.audit import phases
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_git_user_config,
    get_current_files,
    repository_context,
)


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
        github_token=os.getenv("GITHUB_TOKEN"),
        github_username=os.getenv("GITHUB_USERNAME"),
    ):
        # Extract owner/repo from PR URL
        # URL format: https://github.com/owner/repo/pull/123
        parts = pr_url.strip("/").split("/")
        repo_owner = parts[-4]
        repo_name = parts[-3]
        pr_number = int(parts[-1])

        super().__init__(
            client=client,
            prompts=prompts,
            repo_owner=repo_owner,
            repo_name=repo_name,
            pr_url=pr_url,
            pr_number=pr_number,
            staking_key=staking_key,
            pub_key=pub_key,
            staking_signature=staking_signature,
            public_signature=public_signature,
        )
        self.github_token = github_token
        self.github_username = github_username

    def setup(self):
        """Set up repository and workspace."""
        check_required_env_vars(["GITHUB_TOKEN", "GITHUB_USERNAME"])
        validate_github_auth(self.github_token, self.github_username)

        # Get PR info from GitHub
        try:
            gh = Github(self.github_token)
            repo = gh.get_repo(
                f"{self.context['repo_owner']}/{self.context['repo_name']}"
            )
            pr = repo.get_pull(self.context["pr_number"])
            self.context["pr"] = pr
            self.context["base_branch"] = pr.base.ref
            log_key_value("Base branch", self.context["base_branch"])
        except Exception as e:
            log_error(e, "Failed to get PR info")
            raise

        # Set up repository
        log_section("SETTING UP REPOSITORY")
        repo_url = f"https://github.com/{self.context['repo_owner']}/{self.context['repo_name']}"
        fork_name = f"{self.context['repo_name']}-{self.context['repo_owner']}"
        with repository_context(
            repo_url,
            github_token=self.github_token,
            fork_name=fork_name,
        ) as setup_result:
            # Update context with setup results
            self.context["repo_path"] = setup_result["data"]["clone_path"]
            self.original_dir = setup_result["data"]["original_dir"]

            # Enter repo directory
            os.chdir(self.context["repo_path"])

            # Configure Git user info
            setup_git_user_config(self.context["repo_path"])

            # Get current files for context
            self.context["current_files"] = get_current_files()

    def cleanup(self):
        """Cleanup is now handled by repository_context."""
        pass

    def run(self):
        """Execute the audit workflow."""
        try:
            self.setup()

            # Run audit
            audit_phase = phases.AuditPhase(workflow=self)
            audit_result = audit_phase.execute()

            if not audit_result or not audit_result.get("success"):
                log_error(
                    Exception(audit_result.get("error", "No result")),
                    "Audit failed",
                )
                return None

            # Get the validation status
            validated = audit_result["data"].get("validated", False)
            log_key_value("Validation status", "✓ Passed" if validated else "✗ Failed")

            return validated

        except Exception as e:
            log_error(e, "Audit workflow failed")
            raise

        finally:
            self.cleanup()
