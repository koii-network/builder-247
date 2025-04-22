"""Audit workflow implementation."""

import os
from github import Github
from prometheus_swarm.workflows.base import Workflow
from prometheus_swarm.utils.logging import log_section, log_key_value, log_error
from prometheus_swarm.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repository,
    cleanup_repository,
    get_current_files,
)

from src.workflows.audit import phases


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
        github_token="GITHUB_TOKEN",
        github_username="GITHUB_USERNAME",
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
        check_required_env_vars([github_token, github_username])
        self.context["github_token"] = os.getenv(github_token)
        self.context["github_username"] = os.getenv(github_username)

    def setup(self):
        """Set up repository and workspace."""
        validate_github_auth(
            self.context["github_token"], self.context["github_username"]
        )

        # Get PR info from GitHub
        try:
            gh = Github(self.context["github_token"])
            repo = gh.get_repo(
                f"{self.context['repo_owner']}/{self.context['repo_name']}"
            )
            pr = repo.get_pull(self.context["pr_number"])
            self.context["pr"] = pr
            self.context["base_branch"] = pr.base.ref
            log_key_value("Base branch", self.context["base_branch"])
            log_key_value("PR branch", pr.head.ref)
            log_key_value("PR repository", pr.head.repo.full_name)
        except Exception as e:
            log_error(e, "Failed to get PR info")
            raise

        # Set up repository
        log_section("SETTING UP REPOSITORY")
        repo_url = f"https://github.com/{self.context['repo_owner']}/{self.context['repo_name']}"

        result = setup_repository(
            repo_url,
            github_token=self.context["github_token"],
            github_username=self.context["github_username"],
        )
        if not result["success"]:
            raise Exception(result.get("error", "Repository setup failed"))

        # Update context with setup results
        self.context["repo_path"] = result["data"]["clone_path"]
        self.original_dir = result["data"]["original_dir"]

        # Enter repo directory
        os.chdir(self.context["repo_path"])

        # Add remote for PR's repository and fetch the branch
        os.system(
            f"git remote add pr_source https://github.com/{pr.head.repo.full_name}"
        )
        os.system(f"git fetch pr_source {pr.head.ref}")
        os.system("git checkout FETCH_HEAD")

        # Get current files for context
        self.context["current_files"] = get_current_files()

    def cleanup(self):
        """Clean up repository."""
        if hasattr(self, "original_dir") and "repo_path" in self.context:
            cleanup_repository(self.original_dir, self.context["repo_path"])

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
