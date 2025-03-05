"""Merge conflict resolver workflow implementation."""

import os
import time
from github import Github
from src.workflows.base import Workflow
from src.tools.git_operations.implementations import (
    check_for_conflicts,
    get_conflict_info,
)
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.mergeconflict import phases
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repo_directory,
    setup_git_user_config,
    cleanup_repo_directory,
    get_current_files,
    clone_repository,
)


class MergeConflictWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        repo_url,
        target_branch,
        pr_limit=0,
    ):
        # Extract owner and repo name from URL
        # URL format: https://github.com/owner/repo
        parts = repo_url.strip("/").split("/")
        repo_owner = parts[-2]
        repo_name = parts[-1]

        super().__init__(
            client=client,
            prompts=prompts,
            repo_url=repo_url,
            repo_owner=repo_owner,
            repo_name=repo_name,
            target_branch=target_branch,
        )
        self.resolved_conflicts = []
        self.pr_limit = pr_limit

    def setup(self):
        """Set up repository and workspace."""
        check_required_env_vars(["GITHUB_TOKEN", "GITHUB_USERNAME"])
        validate_github_auth(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USERNAME"))

        # Set up repository directory
        repo_path, original_dir = setup_repo_directory()
        self.context["repo_path"] = repo_path
        self.original_dir = original_dir

        # Clone repository
        log_section("CLONING REPOSITORY")
        clone_result = clone_repository(
            self.context["repo_url"],
            self.context["repo_path"],
        )
        if not clone_result["success"]:
            error = clone_result.get("error", "Unknown error")
            log_error(Exception(error), "Clone failed")
            raise Exception(error)

        # Enter repo directory
        os.chdir(self.context["repo_path"])

        # Configure Git user info
        setup_git_user_config(self.context["repo_path"])

        self.context["current_files"] = get_current_files()

    def cleanup(self):
        """Cleanup workspace."""
        # Make sure we're not in the repo directory before cleaning up
        if os.getcwd() == self.context.get("repo_path", ""):
            os.chdir(self.original_dir)

        # Clean up the repository directory
        cleanup_repo_directory(self.original_dir, self.context.get("repo_path", ""))

    def get_open_prs(self):
        """Get all open PRs for the target branch, sorted by creation date."""
        try:
            gh = Github(os.getenv("GITHUB_TOKEN"))
            repo = gh.get_repo(
                f"{self.context['repo_owner']}/{self.context['repo_name']}"
            )

            # Get open PRs targeting the specified branch
            open_prs = list(
                repo.get_pulls(state="open", base=self.context["target_branch"])
            )

            # Sort PRs by creation date (oldest first)
            open_prs.sort(key=lambda pr: pr.created_at)

            log_key_value("Open PRs found", len(open_prs))
            return open_prs
        except Exception as e:
            log_error(e, "Failed to get open PRs")
            return []

    def _try_api_merge(self, pr, repo_full_name):
        """Try to merge a PR using the GitHub API."""
        pr_number = pr.number

        try:
            # Wait for GitHub to calculate mergeable state
            retries = 5
            while retries > 0 and pr.mergeable is None:
                log_key_value(
                    "Merge status", f"Waiting for GitHub (attempts left: {retries})"
                )
                time.sleep(2)  # Wait 2 seconds between checks
                pr.update()  # Refresh the PR data from GitHub
                retries -= 1

            if pr.mergeable is None:
                log_key_value(
                    "Merge status", "GitHub mergeable state calculation timed out"
                )
                return {
                    "success": False,
                    "message": f"Timed out waiting for GitHub to calculate mergeable state for PR #{pr_number}",
                    "data": {
                        "pr_number": pr_number,
                        "conflicts": [],
                        "resolved_conflicts": [],
                    },
                }

            if pr.mergeable:
                log_key_value("Merge strategy", "Direct GitHub API merge")
                try:
                    # Merge the PR directly using the PR object
                    merge_result = pr.merge(merge_method="merge")
                    if merge_result:
                        log_key_value(
                            "Merge result", "Successfully merged via GitHub API"
                        )
                        return {
                            "success": True,
                            "message": f"Successfully merged PR #{pr_number} via GitHub API",
                            "data": {
                                "pr_number": pr_number,
                                "conflicts": [],
                                "resolved_conflicts": [],
                            },
                        }
                except Exception as merge_error:
                    log_key_value("API merge failed", str(merge_error))
                    return {
                        "success": False,
                        "message": f"GitHub API merge failed for PR #{pr_number}: {str(merge_error)}",
                        "data": {
                            "pr_number": pr_number,
                            "conflicts": [],
                            "resolved_conflicts": [],
                        },
                    }
            else:
                # PR has conflicts that need resolution
                log_key_value("Merge status", "PR has conflicts that need resolution")
                return None

        except Exception as e:
            log_error(e, "GitHub API merge check failed")
            return {
                "success": False,
                "message": f"GitHub API error for PR #{pr_number}: {str(e)}",
                "data": {
                    "pr_number": pr_number,
                    "conflicts": [],
                    "resolved_conflicts": [],
                },
            }

    def _resolve_conflicts(self, pr):
        """Resolve conflicts using the LLM."""
        pr_number = pr.number
        source_branch = pr.head.ref

        # Check for conflicts directly using git operations tools
        conflict_result = check_for_conflicts()
        if (
            not conflict_result["success"]
            or not conflict_result["data"]["has_conflicts"]
        ):
            # Abort the merge
            try:
                os.system("git merge --abort")
            except Exception:
                pass
            return {
                "success": False,
                "message": "Merge failed but no conflicts detected",
                "data": {
                    "pr_number": pr_number,
                    "conflicts": [],
                    "resolved_conflicts": [],
                },
            }

        # Get detailed conflict information
        conflict_info = get_conflict_info()
        if not conflict_info["success"]:
            # Abort the merge
            try:
                os.system("git merge --abort")
            except Exception:
                pass
            return {
                "success": False,
                "message": "Failed to get conflict info",
                "data": None,
            }

        # Extract just the list of conflicting files
        conflict_files = list(conflict_info["data"]["conflicts"].keys())
        log_key_value("Conflicting files", ", ".join(conflict_files))

        # Prepare simplified conflict information for the agent
        simplified_conflicts = {
            "files": conflict_files,
            "description": f"Found {len(conflict_files)} files with conflicts",
        }

        # Resolve conflicts using the resolution phase
        resolve_phase = phases.ConflictResolutionPhase(workflow=self)
        self.context["conflicts"] = simplified_conflicts
        resolution_result = resolve_phase.execute()

        if not resolution_result:
            log_error(
                Exception("Conflict resolution phase returned no result"),
                "Conflict resolution failed",
            )
            # Abort the merge
            try:
                os.system("git merge --abort")
            except Exception:
                pass
            return {
                "success": False,
                "message": "Failed to resolve conflicts",
                "data": None,
            }

        # Store resolved conflicts
        resolved_conflicts = resolution_result["data"].get("resolved_conflicts", [])
        self.resolved_conflicts = resolved_conflicts

        # If conflicts were resolved, push the changes to the PR branch
        if resolved_conflicts:
            # Push the resolved changes back to the PR's branch
            push_result = os.system(f"git push origin HEAD:{source_branch}")
            if push_result != 0:
                return {
                    "success": False,
                    "message": f"Failed to push resolved conflicts to PR #{pr_number}",
                    "data": {
                        "pr_number": pr_number,
                        "conflicts": conflict_files,
                        "resolved_conflicts": resolved_conflicts,
                    },
                }

            # Now that conflicts are resolved and pushed, try to merge via GitHub API
            try:
                # Refresh PR data
                pr.update()
                merge_result = pr.merge(merge_method="merge")

                if merge_result:
                    return {
                        "success": True,
                        "message": f"Successfully resolved conflicts and merged PR #{pr_number}",
                        "data": {
                            "pr_number": pr_number,
                            "conflicts": conflict_files,
                            "resolved_conflicts": resolved_conflicts,
                        },
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": (
                        f"Resolved conflicts but failed to merge PR #{pr_number}: {str(e)}"
                    ),
                    "data": {
                        "pr_number": pr_number,
                        "conflicts": conflict_files,
                        "resolved_conflicts": resolved_conflicts,
                    },
                }
        else:
            # Abort the merge
            try:
                os.system("git merge --abort")
            except Exception:
                pass
            return {
                "success": False,
                "message": f"Failed to resolve merge conflicts for PR #{pr_number}",
                "data": {
                    "pr_number": pr_number,
                    "conflicts": conflict_files,
                    "resolved_conflicts": [],
                },
            }

    def merge_pr(self, pr):
        """Merge a single PR, resolving conflicts if needed."""
        try:
            pr_number = pr.number
            source_branch = pr.head.ref

            log_section(f"PROCESSING PR #{pr_number}: {pr.title}")
            log_key_value("Source branch", source_branch)
            log_key_value("Target branch", self.context["target_branch"])

            # Update context with PR-specific information
            self.context["source_branch"] = source_branch
            self.context["pr_number"] = pr_number
            self.context["pr_title"] = pr.title

            # Step 1: Try to merge directly using GitHub API
            api_result = self._try_api_merge(pr, "")
            if api_result:
                return api_result

            # Step 2: If API merge failed due to conflicts, resolve them
            log_key_value("Merge strategy", "Conflict resolution required")
            return self._resolve_conflicts(pr)

        except Exception as e:
            log_error(e, f"Failed to merge PR #{pr.number}")
            # Abort any ongoing merge
            try:
                os.system("git merge --abort")
            except Exception:
                pass
            return {
                "success": False,
                "message": f"Exception while processing PR #{pr.number}: {str(e)}",
                "data": {
                    "pr_number": pr.number,
                    "conflicts": [],
                    "resolved_conflicts": [],
                },
            }

    def run(self):
        """Execute the merge conflict resolver workflow."""
        try:
            self.setup()

            # Get all open PRs and merge them in order
            open_prs = self.get_open_prs()
            if not open_prs:
                return {
                    "success": True,
                    "message": "No open PRs found to merge",
                    "data": {
                        "merged_prs": [],
                        "failed_prs": [],
                    },
                }

            # Apply PR limit if specified
            if self.pr_limit > 0 and len(open_prs) > self.pr_limit:
                log_key_value(
                    "PR limit applied",
                    f"{self.pr_limit} (out of {len(open_prs)} total)",
                )
                open_prs = open_prs[: self.pr_limit]
            else:
                log_key_value("PRs to process", len(open_prs))

            merged_prs = []
            failed_prs = []

            for pr in open_prs:
                result = self.merge_pr(pr)
                if result["success"]:
                    merged_prs.append(result["data"]["pr_number"])
                else:
                    failed_prs.append(pr.number)
                    log_error(
                        Exception(
                            f"Failed to merge PR #{pr.number}: {result.get('message', 'Unknown error')}"
                        ),
                        "Continuing to next PR",
                    )
                    # Continue to the next PR instead of breaking

            return {
                "success": True,
                "message": f"Processed {len(open_prs)} PRs, merged {len(merged_prs)}, failed {len(failed_prs)}",
                "data": {
                    "merged_prs": merged_prs,
                    "failed_prs": failed_prs,
                },
            }
        except Exception as e:
            log_error(e, "Failed to run merge conflict resolver workflow")
            return {
                "success": False,
                "message": f"Failed to run workflow: {str(e)}",
                "data": None,
            }
        finally:
            self.cleanup()
