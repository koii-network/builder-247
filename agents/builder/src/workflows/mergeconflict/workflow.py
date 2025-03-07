"""Merge conflict resolver workflow implementation."""

import os
from src.workflows.base import Workflow
from src.utils.logging import log_key_value, log_error
from src.workflows.mergeconflict import phases
from src.tools.git_operations.implementations import (
    get_conflict_info,
)
from src.workflows.utils import (
    setup_git_user_config,
    setup_repo_directory,
    cleanup_repo_directory,
)


class MergeConflictWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        fork_url,  # URL of our fork where we're accumulating merges
        target_branch,
        pr_url,
    ):
        # Extract source repo info from PR URL
        # URL format: https://github.com/owner/repo/pull/123
        parts = pr_url.strip("/").split("/")
        repo_owner = parts[-4]  # owner is 4th from end in PR URL
        repo_name = parts[-3]  # repo is 3rd from end in PR URL
        pr_number = int(parts[-1])

        super().__init__(
            client=client,
            prompts=prompts,
            repo_url=f"https://github.com/{repo_owner}/{repo_name}",
            repo_owner=repo_owner,
            repo_name=repo_name,
            target_branch=target_branch,
        )
        self.pr_number = pr_number
        self.pr_url = pr_url
        self.fork_url = fork_url
        self.branch_name = f"pr-{self.pr_number}"  # Store branch name for reference

    def setup(self):
        """Set up repository and workspace."""
        try:
            # Set up repository directory
            repo_path, original_dir = setup_repo_directory()
            self.context["repo_path"] = repo_path
            self.context["original_dir"] = original_dir

            # Clone our fork
            auth_url = self.fork_url.replace(
                "https://", f"https://{os.getenv('GITHUB_TOKEN')}@"
            )
            clone_result = os.system(f"git clone {auth_url} {repo_path}")
            if clone_result != 0:
                raise Exception("Failed to clone repository")

            # Change to repo directory
            os.chdir(repo_path)

            # Add source repo as remote
            os.system(f"git remote add source {self.context['repo_url']}")

            # Configure Git user info
            setup_git_user_config(repo_path)

            return True

        except Exception as e:
            log_error(e, "Failed to set up repository")
            return False

    def cleanup(self):
        """Clean up workspace."""
        try:
            cleanup_repo_directory(
                self.context["original_dir"],
                self.context["repo_path"],
            )
        except Exception as e:
            log_error(e, "Failed to clean up repository")

    def run(self):
        """Execute the merge conflict resolver workflow."""
        try:
            if not self.setup():
                return {
                    "success": False,
                    "message": "Failed to set up repository",
                    "data": None,
                }

            # Create and checkout new branch
            log_key_value("Creating branch", self.branch_name)

            # Create new branch from target branch
            os.system(f"git checkout {self.context['target_branch']}")
            os.system(f"git checkout -b {self.branch_name}")

            # Fetch and copy PR changes
            log_key_value("Fetching PR changes", f"PR #{self.pr_number}")
            os.system(f"git fetch source pull/{self.pr_number}/head:pr-temp")
            os.system("git merge --no-commit --no-ff pr-temp")
            os.system('git commit -m "Copy PR changes"')

            # Push branch to our fork
            log_key_value("Pushing branch", self.branch_name)
            # First fetch to ensure we're up to date
            os.system("git fetch origin")
            # Force push since we're creating a new history
            os.system(f"git push -f origin {self.branch_name}")

            # Try to merge target branch
            log_key_value(
                "Action", f"Merging PR branch into {self.context['target_branch']}"
            )
            merge_msg = (
                f'Merge {self.branch_name} into {self.context["target_branch"]} '
                f"(Original PR: {self.pr_url})"
            )
            merge_cmd = (
                f"git checkout {self.context['target_branch']} && "
                f"git merge --no-ff {self.branch_name} "
                f'-m "{merge_msg}" 2>&1'
            )
            merge_output = os.popen(merge_cmd).read()

            # Check for conflicts
            if "Already up to date" in merge_output:
                return {
                    "success": False,
                    "message": f"Failed to properly set up merge state for PR #{self.pr_number}",
                    "data": None,
                }

            # Check for and remove ignored tracked files
            log_key_value("Action", "Checking for ignored tracked files")
            ignored_files = (
                os.popen("git ls-files -ci --exclude-standard").read().strip()
            )
            if ignored_files:
                log_key_value("Found ignored files", ignored_files.replace("\n", ", "))
                os.system("git rm -f $(git ls-files -ci --exclude-standard)")
                os.system("git clean -fdX")  # Also clean untracked ignored files
                os.system("git add -A")

                # Create commit for removed files
                os.system('git commit -m "Remove tracked files that are now ignored"')

            # Check for remaining conflicts
            has_conflicts = "Automatic merge failed" in merge_output
            if has_conflicts:
                log_key_value("Status", "Checking for conflicting files")

                # Get conflict info using the dedicated tool
                conflict_info = get_conflict_info()
                if not conflict_info["success"]:
                    return {
                        "success": False,
                        "message": f"Failed to get conflict info for PR #{self.pr_number}: {conflict_info['message']}",
                        "data": None,
                    }

                # Structure the conflicts in a more useful format for the agent
                conflicts = conflict_info["data"]["conflicts"]
                structured_conflicts = [
                    {
                        "file": file_path,
                        "content": {
                            "ours": content["content"].get("ours", ""),
                            "theirs": content["content"].get("theirs", ""),
                            "ancestor": content["content"].get("ancestor", ""),
                        },
                    }
                    for file_path, content in conflicts.items()
                ]

                log_key_value(
                    "Conflicting files",
                    ", ".join(file_path for file_path, _ in conflicts.items()),
                )

                # Only invoke agent if there are actual conflicts
                if structured_conflicts:
                    # Set up context with structured conflict information
                    self.context["conflicts"] = structured_conflicts

                    # Initialize conflict resolution phase
                    resolve_phase = phases.ConflictResolutionPhase(workflow=self)
                    resolution_result = resolve_phase.execute()

                    if not resolution_result:
                        # Agent was unable to resolve conflicts
                        log_key_value("Result", "Agent was unable to resolve conflicts")
                        try:
                            os.system("git merge --abort")
                        except Exception:
                            pass
                        return {
                            "success": False,
                            "message": f"Failed to resolve conflicts for PR #{self.pr_number}",
                            "data": None,
                        }

            # Push the merged changes to our fork
            push_result = os.system(
                f"git push origin HEAD:{self.context['target_branch']}"
            )
            if push_result != 0:
                return {
                    "success": False,
                    "message": f"Failed to push merged changes for PR #{self.pr_number}",
                    "data": None,
                }

            return {
                "success": True,
                "message": f"Successfully merged PR #{self.pr_number}",
                "data": {
                    "merged_prs": [self.pr_number],
                    "failed_prs": [],
                },
            }

        except Exception as e:
            log_error(e, "Failed to run merge conflict resolver workflow")
            try:
                os.system("git merge --abort")
            except Exception:
                pass
            return {
                "success": False,
                "message": f"Failed to run workflow: {str(e)}",
                "data": None,
            }
        finally:
            self.cleanup()
