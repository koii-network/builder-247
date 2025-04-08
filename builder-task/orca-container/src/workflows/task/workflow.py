"""Task workflow implementation using new workflow structure."""

import os
import time
from github import Github
from git import Repo
from agent_framework.workflows.base import Workflow
from agent_framework.utils.logging import (
    log_section,
    log_key_value,
    log_error,
    log_value,
)
from agent_framework.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repository,
    cleanup_repository,
    get_current_files,
)

from src.workflows.task import phases


class TaskWorkflow(Workflow):

    def __init__(
        self,
        client,
        prompts,
        repo_owner,
        repo_name,
        todo,
        acceptance_criteria,
        staking_key,
        pub_key,
        staking_signature,
        public_signature,
        round_number,
        task_id,
        base_branch,
        max_implementation_attempts=3,
        github_token="GITHUB_TOKEN",
        github_username="GITHUB_USERNAME",
        dependency_pr_urls=None,
    ):
        super().__init__(
            client=client,
            prompts=prompts,
            repo_owner=repo_owner,
            repo_name=repo_name,
            todo=todo,
            acceptance_criteria=acceptance_criteria,
            staking_key=staking_key,
            pub_key=pub_key,
            staking_signature=staking_signature,
            public_signature=public_signature,
            round_number=round_number,
            task_id=task_id,
            base_branch=base_branch,
        )
        check_required_env_vars([github_token, github_username])
        self.max_implementation_attempts = max_implementation_attempts
        self.context["github_token"] = os.getenv(github_token)
        self.context["github_username"] = os.getenv(github_username)
        self.context["dependency_pr_urls"] = dependency_pr_urls or []

    def setup(self):
        """Set up repository and workspace."""
        validate_github_auth(
            self.context["github_token"], self.context["github_username"]
        )
        log_key_value("Base branch", self.context["base_branch"])

        # Set up repository
        log_section("SETTING UP REPOSITORY")

        # Initialize GitHub client
        gh = Github(self.context["github_token"])

        # If we have dependencies, we need to fork from one of them
        if self.context["dependency_pr_urls"]:
            log_section("HANDLING DEPENDENCIES")

            # Get the first dependency's PR to fork from
            dependency_prs = []
            for pr_url in self.context["dependency_pr_urls"]:
                try:
                    # Parse PR URL to get owner, repo, and number
                    parts = pr_url.split("/")
                    owner = parts[-4]
                    repo = parts[-3]
                    pr_number = int(parts[-1])

                    # Get the PR
                    repo = gh.get_repo(f"{owner}/{repo}")
                    pr = repo.get_pull(pr_number)

                    # Verify we can access the head repository and branch
                    head_repo_name = f"{pr.head.repo.owner.login}/{pr.head.repo.name}"
                    log_key_value("Checking head repository", head_repo_name)
                    try:
                        head_repo = gh.get_repo(head_repo_name)
                        # Try to get the branch specifically
                        try:
                            branch = head_repo.get_branch(pr.head.ref)
                            dependency_prs.append(pr)
                        except Exception as branch_e:
                            log_error(
                                branch_e,
                                f"Branch {pr.head.ref} not found in head repo, trying base repo",
                            )
                            raise
                    except Exception as e:
                        log_error(
                            e,
                            f"Cannot access head repository {head_repo_name} or its branch, trying base repository",
                        )
                        # If we can't access the head repo, try using the base repo
                        base_repo_name = (
                            f"{pr.base.repo.owner.login}/{pr.base.repo.name}"
                        )
                        log_key_value("Trying base repository", base_repo_name)
                        base_repo = gh.get_repo(base_repo_name)
                        # Try to get the branch from base repo
                        try:
                            branch = base_repo.get_branch(pr.head.ref)
                            # Use the PR branch from the base repo instead
                            pr.head.repo = base_repo
                            dependency_prs.append(pr)
                        except Exception as branch_e:
                            log_error(
                                branch_e,
                                f"Branch {pr.head.ref} not found in base repo either",
                            )
                            raise

                except Exception as e:
                    log_error(e, f"Failed to get PR from URL {pr_url}")

            if not dependency_prs:
                raise Exception("Could not find PRs for dependencies")

            # Fork from the first dependency's head branch
            base_pr = dependency_prs[0]
            repo_url = (
                base_pr.head.repo.clone_url.replace(".git", "")
                if base_pr.head.repo.clone_url.endswith(".git")
                else base_pr.head.repo.clone_url
            )
            branch = base_pr.head.ref

            log_key_value("Forking from dependency", repo_url)
            log_key_value("Using branch", branch)

            # Set up repository from the dependency's fork and branch
            result = setup_repository(
                repo_url,
                github_token=self.context["github_token"],
                github_username=self.context["github_username"],
                branch=branch,
            )

            if not result["success"]:
                raise Exception(result.get("error", "Repository setup failed"))

            # Update context with setup results
            self.context["repo_path"] = result["data"]["clone_path"]
            self.original_dir = result["data"]["original_dir"]

            # Enter repo directory
            os.chdir(self.context["repo_path"])

            # If we have multiple dependencies, merge them
            if len(dependency_prs) > 1:
                repo = Repo(self.context["repo_path"])
                for pr in dependency_prs[1:]:
                    try:
                        # Add remote for the dependency repo
                        remote_name = f"dependency_{pr.head.sha[:7]}"
                        remote_url = pr.head.repo.clone_url
                        repo.create_remote(remote_name, remote_url)

                        # Fetch the specific branch from the dependency
                        repo.git.fetch(
                            remote_name,
                            f"{pr.head.ref}:refs/remotes/{remote_name}/{pr.head.ref}",
                        )

                        # Merge the dependency branch
                        repo.git.merge(
                            f"{remote_name}/{pr.head.ref}",
                            "--no-ff",
                            "-m",
                            f"Merge dependency from {pr.html_url}",
                        )

                        log_key_value("Merged dependency", pr.html_url)
                    except Exception as e:
                        log_error(e, f"Failed to merge dependency PR {pr.html_url}")
                        raise
        else:
            # No dependencies, fork from the aggregator repo
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

        # Get current files for context
        self.context["current_files"] = get_current_files()

    def cleanup(self):
        """Clean up repository."""
        if hasattr(self, "original_dir") and "repo_path" in self.context:
            cleanup_repository(self.original_dir, self.context["repo_path"])

    def run(self):
        """Execute the task workflow."""
        try:
            self.setup()

            # Create branch
            branch_phase = phases.BranchCreationPhase(workflow=self)
            branch_result = branch_phase.execute()

            if not branch_result:
                return None

            self.context["head_branch"] = branch_result["data"]["branch_name"]

            # Implementation loop
            for attempt in range(self.max_implementation_attempts):
                log_section(
                    f"IMPLEMENTATION ATTEMPT {attempt + 1}/{self.max_implementation_attempts}"
                )

                # Get current files
                self.context["current_files"] = get_current_files()

                # Run implementation
                phase_class = (
                    phases.ImplementationPhase
                    if attempt == 0
                    else phases.FixImplementationPhase
                )
                implementation_phase = phase_class(
                    workflow=self, conversation_id=branch_phase.conversation_id
                )
                implementation_result = implementation_phase.execute()

                if not implementation_result:
                    return None

                # Validate
                validation_phase = phases.ValidationPhase(workflow=self)
                validation_result = validation_phase.execute()

                if not validation_result:
                    continue

                validation_data = validation_result.get("data", {})
                if validation_data.get("validated", False):
                    log_key_value(
                        "Validation successful", "All acceptance criteria met"
                    )
                    break

                previous_issues = "Validation failed for unknown reason"
                # Add details about failed criteria if any
                if validation_data.get("criteria_status"):
                    not_met = validation_data["criteria_status"].get("not_met", [])
                    if not_met:
                        previous_issues = f"Implementation failed for the following criteria: {', '.join(not_met)}"
                        log_key_value("Validation failed", previous_issues)

                self.context["previous_issues"] = previous_issues

                if attempt == self.max_implementation_attempts - 1:
                    log_error(
                        Exception("Failed validation"),
                        "Failed to meet acceptance criteria",
                    )
                    return None

                time.sleep(5)  # Brief pause before retry

            # Create PR
            self.context["current_files"] = get_current_files()

            # Base was already set in setup()
            log_value(
                f"Creating PR from {self.context['head_branch']} to {self.context['base_branch']}",
            )

            pr_phase = phases.PullRequestPhase(
                workflow=self, conversation_id=branch_phase.conversation_id
            )
            pr_result = pr_phase.execute()

            if pr_result.get("success"):
                pr_url = pr_result.get("data", {}).get("pr_url")
                log_key_value("PR created successfully", pr_url)
                return pr_url
            else:
                log_error(Exception(pr_result.get("error")), "PR creation failed")
                return None

        except Exception as e:
            log_error(e, "Error in task workflow")
            raise

        finally:
            self.cleanup()
