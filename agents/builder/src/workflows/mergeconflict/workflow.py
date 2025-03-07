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
from github import Github


class MergeConflictWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        fork_url,  # URL of our fork where we're accumulating merges
        target_branch,
        pr_url,
        github_token,  # Token for GitHub API and Git operations
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
        self.source_fork_url = fork_url  # URL of the fork containing PRs to merge
        self.branch_name = f"pr-{self.pr_number}"  # Store branch name for reference
        self.github_token = github_token

    def setup(self):
        """Set up repository and workspace."""
        try:
            # Set up repository directory
            repo_path, original_dir = setup_repo_directory()
            self.context["repo_path"] = repo_path
            self.context["original_dir"] = original_dir

            # Clone our fork
            gh = Github(self.github_token)
            user = gh.get_user()
            our_fork_url = (
                f"https://github.com/{user.login}/{self.context['repo_name']}"
            )
            self.our_fork_url = our_fork_url  # Store for later use

            auth_url = our_fork_url.replace("https://", f"https://{self.github_token}@")
            clone_result = os.system(f"git clone {auth_url} {repo_path}")
            if clone_result != 0:
                raise Exception("Failed to clone repository")

            # Change to repo directory
            os.chdir(repo_path)

            # Add source repo and source fork as remotes
            os.system(f"git remote add upstream {self.context['repo_url']}")
            os.system(f"git remote add source {self.source_fork_url}")

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

            os.system(f"git checkout {self.context['target_branch']}")

            # Create branch from PR
            log_key_value("Creating branch", self.branch_name)
            os.system(f"git fetch source pull/{self.pr_number}/head:{self.branch_name}")
            os.system(f"git checkout {self.branch_name}")

            # Push branch to our fork
            log_key_value("Pushing branch", self.branch_name)
            auth_url = self.our_fork_url.replace(
                "https://", f"https://{self.github_token}@"
            )
            os.system(f"git remote set-url origin {auth_url}")
            os.system(f"git push -f origin {self.branch_name}")

            # Try to merge PR branch into main
            log_key_value(
                "Action", f"Merging PR branch into {self.context['target_branch']}"
            )
            merge_msg = (
                f'Merge {self.branch_name} into {self.context["target_branch"]} '
                f"(Original PR: {self.pr_url})"
            )
            os.system(f"git checkout {self.context['target_branch']}")
            merge_output = os.popen(
                f"git merge --no-commit --no-ff {self.branch_name} "
                f'-m "{merge_msg}" 2>&1'
            ).read()

            # Check for conflicts
            has_conflicts = "Automatic merge failed" in merge_output
            if has_conflicts:
                log_key_value("Status", "Found conflicts while merging PR changes")

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

            # Commit the merge
            os.system("git commit --no-edit")

            # Push the merged changes to our fork
            push_result = os.system(f"git push origin {self.context['target_branch']}")
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
