"""Merge conflict resolver workflow implementation."""

import os
import time
from github import Github
from src.workflows.base import Workflow
from src.utils.logging import log_key_value, log_error, log_section
from src.workflows.mergeconflict import phases
from src.tools.git_operations.implementations import get_conflict_info
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_git_user_config,
    setup_repo_directory,
    cleanup_repo_directory,
    get_current_files,
    clone_repository,
)
"""Merge conflict resolver workflow implementation."""



class LocalMergeConflictWorkflow(Workflow):
    def __init__(
        self,
        client,
        prompts,
        repo_url,
        target_branch,
        pr_url,
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
        self.pr_url = pr_url

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
        """Get the specific PR from the pr_url."""
        try:
            gh = Github(os.getenv("GITHUB_TOKEN"))
            repo = gh.get_repo(
                f"{self.context['repo_owner']}/{self.context['repo_name']}"
            )
            pr_number = int(self.pr_url.strip("/").split("/")[-1])
            pr = repo.get_pull(pr_number)
            log_key_value("Open PR found", pr_number)
            return pr
        except Exception as e:
            log_error(e, "Failed to get the specific PR")
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

    def _cleanup_ignored_files(self):
        """Delete tracked files that are now ignored by .gitignore."""
        try:
            # First get the updated .gitignore from main
            log_key_value("Checking", "Getting updated .gitignore from main")
            gitignore_content = os.popen(
                f"git show origin/{self.context['target_branch']}:.gitignore"
            ).read()
            if not gitignore_content:
                log_key_value("Warning", "Could not get .gitignore from main branch")
                return False

            # Temporarily update .gitignore with main's version
            log_key_value("Action", "Temporarily updating .gitignore")
            with open(".gitignore", "w") as f:
                f.write(gitignore_content)

            # Now check for tracked files that should be ignored
            log_key_value("Checking", "Finding tracked files that are now ignored")
            ignored_files = (
                os.popen("git ls-files -ci --exclude-standard").read().strip()
            )

            if not ignored_files:
                log_key_value("Result", "No tracked files found that are ignored")
                return True

            # Log what files were found
            log_key_value("Found ignored files", ignored_files.replace("\n", ", "))

            # Try to delete each ignored file
            for file in ignored_files.split("\n"):
                try:
                    os.remove(file)
                    log_key_value("Deleted file", file)
                except Exception as e:
                    log_error(e, f"Failed to delete {file}")
                    return False

            # Check git status before staging
            log_key_value(
                "Git status before staging",
                os.popen("git status --porcelain").read().strip(),
            )

            # Stage the deletions
            stage_result = os.system("git add -A")
            log_key_value(
                "Stage result",
                "Success" if stage_result == 0 else f"Failed with code {stage_result}",
            )

            # Check git status after staging
            log_key_value(
                "Git status after staging",
                os.popen("git status --porcelain").read().strip(),
            )

            # Create commit
            commit_result = os.system(
                'git commit -m "Delete tracked files that are now ignored"'
            )
            log_key_value(
                "Commit result",
                (
                    "Success"
                    if commit_result == 0
                    else f"Failed with code {commit_result}"
                ),
            )

            # Verify the files are actually gone from git's index
            still_tracked = (
                os.popen("git ls-files -ci --exclude-standard").read().strip()
            )
            if still_tracked:
                log_key_value(
                    "Warning", f"Files still tracked after cleanup: {still_tracked}"
                )
                return False

            log_key_value(
                "Cleanup", "Successfully removed all ignored files from tracking"
            )
            return True
        except Exception as e:
            log_error(e, "Failed to cleanup ignored files")
            return False

    def _resolve_conflicts(self, pr):
        """Resolve conflicts using the LLM."""
        pr_number = pr.number
        source_branch = pr.head.ref

        try:
            # Fetch both branches
            log_key_value("Fetching branches", f"PR #{pr_number}")
            os.system("git fetch origin")  # Fetch target branch
            os.system(
                f"git fetch {pr.head.repo.clone_url} {source_branch}"
            )  # Fetch PR branch

            # Checkout PR branch directly
            checkout_result = os.system(
                f"git checkout -b fix-conflicts-{pr_number} FETCH_HEAD"
            )
            if checkout_result != 0:
                return {
                    "success": False,
                    "message": f"Failed to checkout PR branch {source_branch}",
                    "data": None,
                }

            # Try to merge target branch first to get updated .gitignore
            log_key_value(
                "Attempting merge", f"Merging {self.context['target_branch']}"
            )
            merge_output = os.popen(
                f"git merge origin/{self.context['target_branch']} 2>&1"
            ).read()

            # If we see "Already up to date", something went wrong with our merge setup
            if "Already up to date" in merge_output:
                return {
                    "success": False,
                    "message": f"Failed to properly set up merge state for PR #{pr_number}",
                    "data": None,
                }

            # Now that we have the updated .gitignore from main, clean up any ignored files
            log_key_value("Cleanup", "Removing ignored files after merge")

            # First remove any tracked files that are now ignored
            log_key_value("Checking", "Finding tracked files that are now ignored")
            ignored_files = (
                os.popen("git ls-files -ci --exclude-standard").read().strip()
            )
            if ignored_files:
                log_key_value("Found ignored files", ignored_files.replace("\n", ", "))
                # Remove them from git's index and filesystem
                os.system("git rm -f $(git ls-files -ci --exclude-standard)")

            # Then clean up any untracked ignored files
            os.system("git clean -fdX")

            # Stage all changes including deletions
            os.system("git add -A")

            # Check if we have any changes to commit (either from ignored files or merge)
            if "nothing to commit" not in os.popen("git status").read():
                # Create a single merge commit that includes both the merge and cleanup
                commit_result = os.system(
                    "git commit -m \"Merge branch 'main' - includes cleanup of ignored files\""
                )
                if commit_result != 0:
                    return {
                        "success": False,
                        "message": f"Failed to create merge commit for PR #{pr_number}",
                        "data": None,
                    }

            # Now check if we still have conflicts after cleaning up ignored files
            if "Automatic merge failed" not in merge_output:
                log_key_value(
                    "Result", "No real conflicts after cleaning up ignored files"
                )
                # Push the changes back to the PR branch
                auth_url = pr.head.repo.clone_url.replace(
                    "https://", f"https://{os.getenv('GITHUB_TOKEN')}@"
                )
                push_result = os.system(f"git push {auth_url} HEAD:{source_branch}")
                if push_result != 0:
                    return {
                        "success": False,
                        "message": f"Failed to push changes to PR #{pr_number}",
                        "data": None,
                    }

                # Try to merge via GitHub API
                try:
                    # Get a fresh PR object
                    gh = Github(os.getenv("GITHUB_TOKEN"))
                    repo = gh.get_repo(f"{pr.base.repo.full_name}")
                    pr = repo.get_pull(pr_number)

                    # Wait for GitHub to recalculate mergeable state
                    retries = 10
                    while retries > 0:
                        pr = repo.get_pull(pr_number)  # Get fresh PR object
                        if pr.mergeable is True:  # Explicitly check for True
                            break
                        log_key_value(
                            "Merge status",
                            f"Waiting for GitHub (attempts left: {retries})",
                        )
                        time.sleep(5)
                        retries -= 1

                    if pr.mergeable is True:  # Explicitly check for True
                        merge_result = pr.merge(merge_method="merge")
                        if merge_result:
                            return {
                                "success": True,
                                "message": f"Successfully merged PR #{pr_number}",
                                "data": {
                                    "pr_number": pr_number,
                                    "conflicts": [],
                                },
                            }

                    log_key_value(
                        "Error", f"PR #{pr_number} not mergeable after cleanup"
                    )
                    return {
                        "success": False,
                        "message": f"PR #{pr_number} not mergeable after cleanup",
                        "data": None,
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Failed to merge PR #{pr_number} via GitHub API: {str(e)}",
                        "data": None,
                    }

            # Abort the merge if we got here somehow
            try:
                os.system("git merge --abort")
            except Exception:
                pass
            return {
                "success": False,
                "message": f"Failed to resolve merge conflicts for PR #{pr_number}",
                "data": {
                    "pr_number": pr_number,
                    "conflicts": [],
                },
            }

        except Exception as e:
            log_error(e, "Failed to set up merge state")
            return {
                "success": False,
                "message": f"Failed to set up merge state: {str(e)}",
                "data": None,
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

            # Step 1: Check if PR can be merged automatically via GitHub API
            retries = 5
            while retries > 0 and pr.mergeable is None:
                log_key_value(
                    "Status",
                    f"Waiting for GitHub mergeable state (attempts left: {retries})",
                )
                time.sleep(2)
                pr.update()
                retries -= 1

            can_merge_automatically = pr.mergeable is True  # Explicitly check for True
            log_key_value("Can merge automatically", str(can_merge_automatically))

            # Step 2: If not automatically mergeable, check out PR and attempt merge
            if not can_merge_automatically:
                # Fetch and checkout PR branch
                log_key_value("Action", "Checking out PR branch")
                os.system("git fetch origin")  # Fetch target branch
                os.system(
                    f"git fetch {pr.head.repo.clone_url} {source_branch}"
                )  # Fetch PR branch

                checkout_result = os.system(
                    f"git checkout -b fix-conflicts-{pr_number} FETCH_HEAD"
                )
                if checkout_result != 0:
                    return {
                        "success": False,
                        "message": f"Failed to checkout PR branch {source_branch}",
                        "data": None,
                    }

                # Try to merge target branch
                log_key_value("Action", f"Merging {self.context['target_branch']}")
                merge_output = os.popen(
                    f"git merge origin/{self.context['target_branch']} 2>&1"
                ).read()

                if "Already up to date" in merge_output:
                    return {
                        "success": False,
                        "message": f"Failed to properly set up merge state for PR #{pr_number}",
                        "data": None,
                    }

                # Step 3: Check for and remove ignored tracked files
                log_key_value("Action", "Checking for ignored tracked files")
                ignored_files = (
                    os.popen("git ls-files -ci --exclude-standard").read().strip()
                )
                if ignored_files:
                    log_key_value(
                        "Found ignored files", ignored_files.replace("\n", ", ")
                    )
                    os.system("git rm -f $(git ls-files -ci --exclude-standard)")
                    os.system("git clean -fdX")  # Also clean untracked ignored files
                    os.system("git add -A")

                # Step 4: Check for remaining conflicts
                has_conflicts = "Automatic merge failed" in merge_output
                if has_conflicts:
                    log_key_value("Status", "Checking for conflicting files")

                    # Get conflict info using the dedicated tool
                    conflict_info = get_conflict_info()
                    if not conflict_info["success"]:
                        return {
                            "success": False,
                            "message": f"Failed to get conflict info for PR #{pr_number}: {conflict_info['message']}",
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
                            # Agent was unable to resolve conflicts or determined target branch is better
                            log_key_value(
                                "Result", "Agent determined PR should not be merged"
                            )
                            try:
                                os.system("git merge --abort")
                            except Exception:
                                pass
                            return {
                                "success": False,
                                "message": f"PR #{pr_number} should be closed without merging",
                                "data": {"pr_number": pr_number, "should_close": True},
                            }

                # Step 5: Create merge commit if we had to perform manual merge
                if not can_merge_automatically:
                    if "nothing to commit" not in os.popen("git status").read():
                        commit_result = os.system(
                            "git commit -m \"Merge branch 'main'\""
                        )
                        if commit_result != 0:
                            return {
                                "success": False,
                                "message": f"Failed to create merge commit for PR #{pr_number}",
                                "data": None,
                            }

                    # Push changes back to PR branch
                    auth_url = pr.head.repo.clone_url.replace(
                        "https://", f"https://{os.getenv('GITHUB_TOKEN')}@"
                    )
                    push_result = os.system(f"git push {auth_url} HEAD:{source_branch}")
                    if push_result != 0:
                        return {
                            "success": False,
                            "message": f"Failed to push changes to PR #{pr_number}",
                            "data": None,
                        }

                    # Wait for GitHub to update PR state
                    retries = 10
                    while retries > 0:
                        pr = pr.base.repo.get_pull(pr_number)  # Get fresh PR object
                        if pr.mergeable is True:  # Explicitly check for True
                            break
                        log_key_value(
                            "Status",
                            f"Waiting for GitHub to update PR state (attempts left: {retries})",
                        )
                        time.sleep(5)
                        retries -= 1

            # Step 6: Merge the PR
            try:
                merge_result = pr.merge(merge_method="merge")
                if merge_result:
                    log_key_value("Status", f"Successfully merged PR #{pr_number}")
                    return {
                        "success": True,
                        "message": f"Successfully merged PR #{pr_number}",
                        "data": {"pr_number": pr_number},
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to merge PR #{pr_number}: {str(e)}",
                    "data": None,
                }

            return {
                "success": False,
                "message": f"Failed to merge PR #{pr_number} - PR not mergeable",
                "data": None,
            }

        except Exception as e:
            log_error(e, f"Failed to process PR #{pr.number}")
            try:
                os.system("git merge --abort")
            except Exception:
                pass
            return {
                "success": False,
                "message": f"Exception while processing PR #{pr.number}: {str(e)}",
                "data": None,
            }

    def run(self):
        """Execute the merge conflict resolver workflow."""
        merged_prs = []
        failed_prs = []
        try:
            self.setup()
            open_pr = self.get_open_prs()
            result = self.merge_pr(open_pr)
            if result["success"]:
                merged_prs.append(result["data"]["pr_number"])
            else:
                failed_prs.append(open_pr.number)
                log_error(
                    Exception(
                        f"Failed to merge PR #{open_pr.number}: {result.get('message', 'Unknown error')}"
                    ),
                    "Continuing to next PR",
                )
                    # Continue to the next PR instead of breaking

            return {
                "success": True,
                "message": f"Successfully merged PR #{open_pr.number}",
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

class RemoteMergeConflictWorkflow(Workflow):
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
