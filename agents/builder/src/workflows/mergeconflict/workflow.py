"""Merge conflict resolver workflow implementation."""

import os
from github import Github
from src.workflows.base import Workflow
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.utils import repository_context, get_fork_name
from src.workflows.mergeconflict.phases import (
    ConflictResolutionPhase,
    CreatePullRequestPhase,
)
from src.tools.github_operations.parser import extract_section
from src.utils.signatures import verify_and_parse_signature


class MergeConflictWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        source_fork_url,  # URL of fork containing PRs (first level fork)
        source_branch,  # Branch on source fork containing PRs to merge (e.g. round-123-task-456)
        is_source_fork_owner=False,  # True if we own the source fork, False if we need to fork it
        staking_key=None,  # Leader's staking key
        pub_key=None,  # Leader's public key
        staking_signature=None,  # Leader's staking signature
        public_signature=None,  # Leader's public signature
        task_id=None,  # Task ID for signature validation
        round_number=None,  # Round number for signature validation
        staking_keys=None,  # Distribution list for signature validation
        github_token=os.getenv("GITHUB_TOKEN"),
        github_username=os.getenv("GITHUB_USERNAME"),
    ):
        # Extract source repo info from source fork URL
        parts = source_fork_url.strip("/").split("/")
        source_fork_owner = parts[-2]

        super().__init__(
            client=client,
            prompts=prompts,
        )

        self.source_fork_owner = (
            source_fork_owner  # Only property we need for branch naming
        )
        self.is_source_fork_owner = is_source_fork_owner
        self.task_id = task_id
        self.round_number = round_number
        self.staking_keys = staking_keys or []
        self.github_token = github_token
        self.github_username = github_username

        # Initialize context with source info
        self.context.update(
            {
                "source_fork": {
                    "url": source_fork_url,
                    "owner": source_fork_owner,
                    "name": parts[-1],
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
        gh = Github(self.github_token)
        source_fork = gh.get_repo(f"{source_fork_owner}/{parts[-1]}")
        upstream = source_fork.parent

        self.context["upstream"] = {
            "url": upstream.html_url,
            "owner": upstream.owner.login,
            "name": upstream.name,
            "default_branch": upstream.default_branch,
        }

    def validate_pr_signatures(self, pr):
        """Validate signatures in a PR against the distribution list.

        Args:
            pr: GitHub PR object to validate

        Returns:
            bool: True if all required signatures are valid, False otherwise
        """
        # Skip validation if we don't have task_id or round_number
        if not self.task_id or not self.round_number:
            return True

        # The distribution list is already filtered to only include eligible nodes
        # Just verify signature for each node in the list
        for submitter_staking_key in self.staking_keys:
            # Extract signatures using parser
            staking_signature_section = extract_section(pr.body, "STAKING_KEY")

            if not staking_signature_section:
                print(f"Missing staking key signature in PR #{pr.number}")
                return False

            # Parse the signature sections to get the specific staking key's signatures
            staking_parts = staking_signature_section.strip().split(":")

            if (
                len(staking_parts) != 2
                or staking_parts[0].strip() != submitter_staking_key
            ):
                print(
                    f"Invalid or missing staking signature for staking key {submitter_staking_key} in PR #{pr.number}"
                )
                return False

            staking_signature = staking_parts[1].strip()

            # Verify signature and validate payload
            expected_values = {
                "taskId": self.task_id,
                "roundNumber": self.round_number,
                "stakingKey": submitter_staking_key,
            }

            result = verify_and_parse_signature(
                staking_signature, submitter_staking_key, expected_values
            )

            if result.get("error"):
                print(f"Invalid signature in PR #{pr.number}: {result['error']}")
                return False

        return True

    def setup(self):
        """Set up repository and workspace."""
        try:
            # Use repository_context to handle forking and cloning
            log_section("SETTING UP REPOSITORY")
            repo_url = self.context["source_fork"]["url"]
            gh = Github(self.github_token)
            fork_name = get_fork_name(self.source_fork_owner, repo_url, github=gh)
            with repository_context(
                repo_url,
                github_token=self.github_token,
                fork_name=fork_name,
            ) as setup_result:
                # Add working fork info to context
                self.context["working_fork"] = {
                    "url": setup_result["data"]["fork_url"],
                    "owner": setup_result["data"]["owner"],
                    "name": self.context["source_fork"]["name"],
                }

                # Set required context variables for PR creation
                self.context["repo_owner"] = self.context["upstream"]["owner"]
                self.context["repo_name"] = self.context["upstream"]["name"]

                # Change to repo directory
                self.context["repo_path"] = setup_result["data"]["clone_path"]
                os.chdir(setup_result["data"]["clone_path"])

                # Configure source remote if we don't own the source fork
                if not self.is_source_fork_owner:
                    os.system(
                        f"git remote add source {self.context['source_fork']['url']}"
                    )
                    os.system("git fetch source")

                # Create head branch from source branch
                source_branch = self.context["source_fork"]["branch"]
                head_branch = self.context["head_branch"]

                # Checkout source branch first
                os.system(
                    f"git fetch {'origin' if self.is_source_fork_owner else 'source'} {source_branch}"
                )
                os.system(f"git checkout -b {head_branch} FETCH_HEAD")
                # Push head branch to our fork
                os.system(f"git push -u origin {head_branch}")

                return True

        except Exception as e:
            log_error(e, "Failed to set up repository")
            return False

    def merge_pr(self, pr_url, pr_title):
        """Merge a single PR into the head branch.

        Args:
            pr_url: URL of the original PR in the source fork
            pr_title: Title of the PR to merge
        """
        # Extract PR info from URL
        parts = pr_url.strip("/").split("/")
        pr_number = int(parts[-1])
        pr_repo_owner = parts[-4]
        pr_repo_name = parts[-3]

        try:
            # Create unique branch name for PR content
            pr_branch = f"{pr_repo_owner}-{pr_repo_name}-pr-{pr_number}"

            if self.is_source_fork_owner:
                # We own the source fork, just checkout PR branch
                os.system(f"git checkout {pr_branch}")
            else:
                # Fetch PR from source fork into named branch
                os.system(f"git fetch source pull/{pr_number}/head:{pr_branch}")
                os.system(f"git checkout {pr_branch}")

            # Push PR branch to our fork for auditing
            os.system(f"git push origin {pr_branch}")

            # Try to merge into head branch
            os.system(f"git checkout {self.context['head_branch']}")
            merge_output = os.popen(
                f"git merge --no-commit --no-ff {pr_branch} 2>&1"
            ).read()

            # Handle conflicts through the ConflictResolutionPhase
            if "CONFLICT" in merge_output:
                resolution_phase = ConflictResolutionPhase(workflow=self)
                resolution_result = resolution_phase.execute()
                if not resolution_result or not resolution_result.get("success"):
                    raise Exception("Failed to resolve conflicts")

            # Commit the merge
            os.system('git commit -m "Merge PR #{pr_number}"')
            os.system(f"git push origin {self.context['head_branch']}")

            # Track merged PR
            self.context["merged_prs"].append(pr_number)  # For type compatibility
            self.context["pr_details"].append(
                {
                    "number": pr_number,
                    "title": pr_title,
                    "url": pr_url,  # Original PR URL
                }
            )
            return {"success": True, "message": f"Successfully merged PR #{pr_number}"}

        except Exception as e:
            log_error(e, f"Failed to merge PR #{pr_number}")
            return {"success": False, "message": str(e)}

    def run(self):
        """Execute the merge conflict workflow."""
        try:
            if not self.setup():
                return {"success": False, "message": "Setup failed"}

            # Get list of PRs to process
            gh = Github(self.github_token)
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

            # Filter PRs based on signature validation
            valid_prs = [pr for pr in open_prs if self.validate_pr_signatures(pr)]
            log_key_value("PRs with valid signatures", len(valid_prs))

            # Process each valid PR
            for pr in valid_prs:
                log_section(f"Processing PR #{pr.number}")
                self.merge_pr(pr.html_url, pr.title)

            # Create consolidated PR if we have any merged PRs
            if self.context["merged_prs"]:
                pr_phase = CreatePullRequestPhase(workflow=self)
                try:
                    pr_result = pr_phase.execute()
                    if not pr_result:
                        log_error(
                            Exception("PR creation phase returned None"),
                            "PR creation failed",
                        )
                        return None

                    if pr_result.get("success"):
                        pr_url = pr_result.get("data", {}).get("pr_url")
                        log_key_value("PR created successfully", pr_url)
                        return pr_url
                    else:
                        log_error(
                            Exception(pr_result.get("error")), "PR creation failed"
                        )
                        return None
                except Exception as e:
                    log_error(e, "PR creation phase failed")
                    return None

            return None

        except Exception as e:
            log_error(e, "Error in task workflow")
            raise

        finally:
            self.cleanup()
