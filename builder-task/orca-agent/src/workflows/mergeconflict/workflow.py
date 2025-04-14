"""Merge conflict resolver workflow implementation."""

import os
from github import Github
from prometheus_swarm.workflows.base import Workflow
from prometheus_swarm.utils.logging import log_section, log_key_value, log_error
from prometheus_swarm.tools.github_operations.parser import extract_section
from prometheus_swarm.utils.signatures import verify_and_parse_signature
from prometheus_swarm.workflows.utils import (
    check_required_env_vars,
    setup_repository,
    cleanup_repository,
    get_current_files,
)
from src.workflows.mergeconflict.phases import (
    ConflictResolutionPhase,
    CreatePullRequestPhase,
    TestVerificationPhase,
)


class MergeConflictWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        source_fork_url,  # URL of fork containing PRs (first level fork)
        source_branch,  # Branch on source fork containing PRs to merge (e.g. round-123-task-456)
        staking_key=None,  # Leader's staking key
        pub_key=None,  # Leader's public key
        staking_signature=None,  # Leader's staking signature
        public_signature=None,  # Leader's public signature
        task_id=None,  # Task ID for signature validation
        pr_list=None,  # dict of {staking_key: pr_url}
        github_token="GITHUB_TOKEN",
        github_username="GITHUB_USERNAME",
        expected_branch=None,  # Branch where PRs are located
    ):
        # Extract source repo info from source fork URL
        parts = source_fork_url.strip("/").split("/")
        source_fork_owner = parts[-2]
        source_repo_name = parts[-1]

        super().__init__(
            client=client,
            prompts=prompts,
        )

        # Initialize conversation ID
        self.conversation_id = None

        check_required_env_vars([github_token, github_username])
        self.context["github_token"] = os.getenv(github_token)
        consolidation_username = os.getenv(github_username)
        self.context["github_username"] = consolidation_username

        self.source_fork_owner = source_fork_owner
        # We own the source fork if our consolidation username matches the source fork owner
        self.is_source_fork_owner = consolidation_username == source_fork_owner
        self.task_id = task_id
        self.pr_list = pr_list

        # Verify source branch format matches expected_branch
        if source_branch != expected_branch:
            raise ValueError(
                f"Source branch {source_branch} does not match expected format {expected_branch}"
            )

        # Initialize context with source info
        self.context.update(
            {
                "source_fork": {
                    "url": source_fork_url,
                    "owner": source_fork_owner,
                    "name": source_repo_name,
                    "branch": source_branch,
                },
                "head_branch": f"{source_branch}-merged",  # Branch where we'll merge all PRs
                "merged_prs": [],  # List of PR numbers for type compatibility
                "pr_details": [],  # List of {number, title, url} for merged PRs
                # Add leader signature info to context
                "staking_key": staking_key,
                "pub_key": pub_key,
                "staking_signature": staking_signature,
                "public_signature": public_signature,
            }
        )

        # Get upstream repo info and add to context
        gh = Github(self.context["github_token"])
        source_fork = gh.get_repo(f"{source_fork_owner}/{source_repo_name}")
        upstream = source_fork.parent

        self.context["upstream"] = {
            "url": upstream.html_url,
            "owner": upstream.owner.login,
            "name": upstream.name,
            "default_branch": upstream.default_branch,
        }

    def validate_pr_for_merge(self, pr):
        """Validate a PR's signatures and check if it should be merged.

        Args:
            pr: GitHub PR object to validate

        Returns:
            tuple: (should_merge: bool, staking_key: str)
            should_merge is False if PR should be skipped, True if it should be merged
            staking_key is returned if validation passes to avoid extracting it twice

        Raises:
            ValueError: If validation fails with details about the failure
        """
        # Extract signatures using parser
        staking_signature_section = extract_section(pr.body, "STAKING_KEY")

        if not staking_signature_section:
            raise ValueError(f"PR #{pr.number} is missing staking key signature")

        # Parse the signature sections to get the staking key
        staking_parts = staking_signature_section.strip().split(":")

        if len(staking_parts) != 2:
            raise ValueError(f"PR #{pr.number} has invalid signature format")

        submitter_staking_key = staking_parts[0].strip()
        staking_signature = staking_parts[1].strip()

        # Check if this staking key is in our pr_list
        if submitter_staking_key not in self.pr_list:
            return False

        # Check if this PR's URL is in the list for this staking key
        pr_urls = self.pr_list[submitter_staking_key]
        if not isinstance(pr_urls, list):
            pr_urls = [pr_urls]  # Handle single URL case

        if pr.html_url not in pr_urls:
            return False

        # Verify signature and validate payload
        expected_values = {
            "taskId": self.task_id,
            "stakingKey": submitter_staking_key,
        }

        result = verify_and_parse_signature(
            staking_signature, submitter_staking_key, expected_values
        )

        if result.get("error"):
            raise ValueError(f"Invalid signature in PR #{pr.number}: {result['error']}")

        return True

    def setup(self):
        """Set up repository and workspace."""
        try:
            # Set up repository
            log_section("SETTING UP REPOSITORY")
            repo_url = self.context["source_fork"]["url"]

            # If we own the source fork, clone it directly
            # Otherwise, let setup_repository fork it
            if self.is_source_fork_owner:
                result = setup_repository(
                    repo_url,
                    github_token=self.context["github_token"],
                    github_username=self.context["github_username"],
                    skip_fork=True,  # Don't fork if we own the source
                )
            else:
                result = setup_repository(
                    repo_url,
                    github_token=self.context["github_token"],
                    github_username=self.context["github_username"],
                )

            if not result["success"]:
                raise Exception(result.get("error", "Repository setup failed"))

            # Add working fork info to context
            if self.is_source_fork_owner:
                self.context["working_fork"] = {
                    "url": repo_url,  # We're working directly on the source fork
                    "owner": self.context["source_fork"]["owner"],
                    "name": self.context["source_fork"]["name"],
                }
            else:
                self.context["working_fork"] = {
                    "url": result["data"]["fork_url"],
                    "owner": result["data"]["fork_owner"],
                    "name": result["data"]["fork_name"],
                }

            # Set required context variables for PR creation
            self.context["repo_owner"] = self.context["upstream"]["owner"]
            self.context["repo_name"] = self.context["upstream"]["name"]

            # Change to repo directory
            self.context["repo_path"] = result["data"]["clone_path"]
            os.chdir(self.context["repo_path"])

            # Configure source remote if we don't own the source fork
            if not self.is_source_fork_owner:
                os.system(f"git remote add source {self.context['source_fork']['url']}")
                os.system("git fetch source")

            # Create merge branch from source branch
            source_branch = self.context["source_fork"]["branch"]
            head_branch = self.context["head_branch"]

            # Fetch source branch and create merge branch from it
            os.system(
                f"git fetch {'origin' if self.is_source_fork_owner else 'source'} {source_branch}"
            )
            os.system(f"git checkout -b {head_branch} FETCH_HEAD")
            os.system(f"git push origin {head_branch}")

            return True

        except Exception as e:
            log_error(e, "Failed to set up repository")
            return False

    def merge_pr(self, pr_url, pr_title):
        """Merge a single PR into the head branch."""
        # Extract PR info from URL
        parts = pr_url.strip("/").split("/")
        pr_number = int(parts[-1])
        pr_repo_owner = parts[-4]
        pr_repo_name = parts[-3]

        try:
            # Get the actual PR author from the GitHub API
            gh = Github(self.context["github_token"])
            repo = gh.get_repo(f"{pr_repo_owner}/{pr_repo_name}")
            pr = repo.get_pull(pr_number)
            pr_author = pr.user.login  # Get the actual author's GitHub username

            print(f"PR #{pr_number} created by GitHub user: {pr_author}")

            # Create unique branch name for PR content
            pr_branch = f"pr-{pr_number}-{pr_repo_owner}-{pr_repo_name}"
            print(
                f"Attempting to merge PR #{pr_number} from {pr_repo_owner}/{pr_repo_name}"
            )
            print(f"Creating branch: {pr_branch}")
            print(f"Current directory: {os.getcwd()}")
            print("Git remotes:")
            remotes_output = os.popen("git remote -v 2>&1").read()
            print(remotes_output)

            # Always create a new branch with PR contents, regardless of fork ownership
            if self.is_source_fork_owner:
                # Even though we own the fork, create a new branch from the PR's HEAD
                print("Fetching PR from origin (we own the fork)")
                fetch_output = os.popen(
                    f"git fetch origin pull/{pr_number}/head 2>&1"
                ).read()
                print(f"Fetch output: {fetch_output}")
                checkout_output = os.popen(
                    f"git checkout -b {pr_branch} FETCH_HEAD 2>&1"
                ).read()
                print(f"Checkout output: {checkout_output}")
            else:
                # Fetch PR from source fork into new branch
                print("Fetching PR from source remote")
                fetch_output = os.popen(
                    f"git fetch source pull/{pr_number}/head 2>&1"
                ).read()
                print(f"Fetch output: {fetch_output}")
                checkout_output = os.popen(
                    f"git checkout -b {pr_branch} FETCH_HEAD 2>&1"
                ).read()
                print(f"Checkout output: {checkout_output}")

            # Push PR branch to our fork for auditing
            print(f"Pushing branch {pr_branch} to origin")
            push_output = os.popen(f"git push origin {pr_branch} 2>&1").read()
            print(f"Push output: {push_output}")

            # Try to merge into head branch
            print(f"Checking out head branch: {self.context['head_branch']}")
            checkout_output = os.popen(
                f"git checkout {self.context['head_branch']} 2>&1"
            ).read()
            print(f"Checkout output: {checkout_output}")

            print(f"Attempting to merge {pr_branch}")
            merge_output = os.popen(
                f"git merge --no-commit --no-ff {pr_branch} 2>&1"
            ).read()
            print(f"Merge output: {merge_output}")

            # Handle conflicts through the ConflictResolutionPhase
            if "CONFLICT" in merge_output:
                print("Merge conflicts detected, attempting resolution")
                self.context["current_files"] = get_current_files()
                resolution_phase = ConflictResolutionPhase(
                    workflow=self,
                    conversation_id=getattr(
                        self, "conversation_id", None
                    ),  # Get conversation_id if it exists
                )
                resolution_result = resolution_phase.execute()

                # Store the conversation ID for future phases
                self.conversation_id = resolution_phase.conversation_id

                if not resolution_result or not resolution_result.get("success"):
                    raise Exception("Failed to resolve conflicts")
                print("Successfully resolved conflicts")

            # Commit the merge with branch name and PR URL
            print("Committing merge")
            commit_output = os.popen(
                f'git commit -m "Merged branch {pr_branch} for PR {pr_url}" 2>&1'
            ).read()
            print(f"Commit output: {commit_output}")

            print(f"Pushing merged changes to {self.context['head_branch']}")
            push_output = os.popen(
                f"git push origin {self.context['head_branch']} 2>&1"
            ).read()
            print(f"Push output: {push_output}")

            # Only track successfully merged PRs
            self.context["merged_prs"].append(pr_number)
            self.context["pr_details"].append(
                {
                    "number": pr_number,
                    "title": pr_title,
                    "url": pr_url,
                    "source_owner": pr_author,  # Use the actual PR author instead of repo owner
                }
            )
            print(f"Successfully merged PR #{pr_number}")
            return {"success": True, "message": f"Successfully merged PR #{pr_number}"}

        except Exception as e:
            log_error(e, f"Failed to merge PR #{pr_number}")
            print(f"Current directory: {os.getcwd()}")
            print("Git status:")
            status_output = os.popen("git status 2>&1").read()
            print(status_output)
            print("Git branch:")
            branch_output = os.popen("git branch 2>&1").read()
            print(branch_output)
            print("Git log:")
            log_output = os.popen("git log --oneline -n 5 2>&1").read()
            print(log_output)
            return {"success": False, "message": str(e)}

    def run(self):
        """Execute the merge conflict workflow."""
        try:
            if not self.setup():
                log_error(Exception("Setup failed"), "Repository setup failed")
                return None

            # Get list of PRs to process
            gh = Github(self.context["github_token"])
            source_fork = gh.get_repo(
                f"{self.source_fork_owner}/{self.context['source_fork']['name']}"
            )
            open_prs = list(
                source_fork.get_pulls(
                    state="open", base=self.context["source_fork"]["branch"]
                )
            )

            # Sort PRs by creation date (oldest first)
            open_prs.sort(key=lambda pr: pr.created_at)
            log_key_value("PRs to process", len(open_prs))
            for pr in open_prs:
                print(f"Found PR #{pr.number}: {pr.title} from {pr.user.login}")

            if not open_prs:
                log_error(Exception("No open PRs found"), "No PRs to process")
                return None

            # Process each PR in chronological order
            for pr in open_prs:
                log_section(f"Processing PR #{pr.number}")

                try:
                    # Validate PR and check if we should merge it
                    should_merge = self.validate_pr_for_merge(pr)
                    if not should_merge:
                        print(
                            f"Skipping PR #{pr.number} - not in PR list or wrong staking key"
                        )
                        continue

                    # If we get here, validation passed and we should merge
                    result = self.merge_pr(pr_url=pr.html_url, pr_title=pr.title)
                    if not result["success"]:
                        log_error(
                            Exception(result.get("message", "Unknown error")),
                            f"Failed to merge PR #{pr.number}",
                        )
                        return None

                except ValueError as e:
                    log_error(e, f"Validation failed for PR #{pr.number}")
                    return None

            if not self.context["merged_prs"]:
                log_error(
                    Exception("No PRs were merged"), "No PRs were successfully merged"
                )
                return None

            # Run tests and fix any issues
            print("\nRunning test verification phase")
            self.context["current_files"] = get_current_files()
            test_phase = TestVerificationPhase(
                workflow=self, conversation_id=self.conversation_id
            )
            test_result = test_phase.execute()
            if not test_result or not test_result.get("success"):
                log_error(
                    Exception(test_result.get("error", "Test verification failed")),
                    "Tests failed after merging PRs",
                )
                return None

            # Store the conversation ID from test phase
            self.conversation_id = test_phase.conversation_id

            # Create PR if tests pass
            print("\nCreating consolidated PR")
            pr_phase = CreatePullRequestPhase(
                workflow=self, conversation_id=self.conversation_id
            )
            try:
                pr_result = pr_phase.execute()
                if not pr_result:
                    log_error(
                        Exception("PR creation phase returned None"),
                        "PR creation failed - no result returned",
                    )
                    return None

                if pr_result.get("success"):
                    pr_url = pr_result.get("data", {}).get("pr_url")
                    if not pr_url:
                        log_error(
                            Exception("No PR URL in successful result"),
                            "PR creation succeeded but no URL returned",
                        )
                        return None
                    log_key_value("PR created successfully", pr_url)
                    return pr_url
                else:
                    error = pr_result.get("error", "Unknown error")
                    log_error(Exception(error), "PR creation failed with error")
                    return None
            except Exception as e:
                log_error(e, "PR creation phase failed with exception")
                return None

            return None

        except Exception as e:
            log_error(e, "Error in merge conflict workflow")
            raise

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up repository."""
        if hasattr(self, "original_dir") and "repo_path" in self.context:
            cleanup_repository(self.original_dir, self.context["repo_path"])
