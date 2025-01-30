"""Module for GitHub operations."""

import os
from pathlib import Path
from typing import Dict, Any
from github import Github, Auth, GithubException
from git import Repo
from dotenv import load_dotenv
from .pr_template import validate_pr_description
from src.tools.git_operations import (
    clone_repository,
    add_remote,
    fetch_remote,
    pull_remote,
    push_remote,
    can_access_repository,
    check_for_conflicts,
    get_conflict_info,
    create_merge_commit,
    resolve_conflict,
    commit_and_push,
)
from src.tools.file_operations import copy_file

import time
import requests
import shutil

# Load environment variables from .env file
load_dotenv()


class GitHubOperations:
    """Class for handling GitHub operations."""

    def __init__(self):
        """Initialize GitHub operations."""
        self.token = os.environ.get("GITHUB_TOKEN")
        self.username = os.environ.get("GITHUB_USERNAME")
        if not self.token:
            raise ValueError("Missing GITHUB_TOKEN")
        if not self.username:
            raise ValueError("Missing GITHUB_USERNAME")
        self.gh = Github(auth=Auth.Token(self.token))

    def get_pr_template(self) -> str:
        """
        Get the PR template content. If the template doesn't exist in .github/,
        copy it from docs/agent/pr_template.md.

        Returns:
            str: The PR template content
        """
        template_path = Path(".github/pull_request_template.md")
        source_template = Path("docs/agent/pr_template.md")

        # If template doesn't exist, try to copy it from source
        if not template_path.exists():
            if not source_template.exists():
                raise FileNotFoundError("Source PR template file not found")

            # Create .github directory and copy template
            template_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source_template), str(template_path))

        # Read and return the template content
        return template_path.read_text()

    def fork_repository(self, repo_full_name: str, target_dir: str = None) -> Dict[str, Any]:
        """
        Fork a repository and clone it locally.

        Args:
            repo_full_name (str): Full name of the repository (e.g. "owner/repo")
            target_dir (str, optional): Directory where to clone the fork.
                                      If None, uses current directory

        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation succeeded
                - fork_url (str): URL of the forked repository if successful
                - repo (Repo): GitPython Repo instance if successful
                - error (str): Error message if unsuccessful
        """
        try:
            print(f"Getting repository: {repo_full_name}")
            repo = self.gh.get_repo(repo_full_name)
            print(f"Creating fork of repository: {repo.full_name}")
            fork = self.gh.get_user().create_fork(repo)
            print(f"Fork created: {fork.full_name}")
            print(f"Fork URL: {fork.clone_url}")

            # Wait for GitHub to propagate the fork
            print("Waiting for fork to be propagated...")
            time.sleep(5)

            # Clone the fork
            target_dir = target_dir or os.path.basename(fork.name)
            print(f"Cloning fork to {target_dir}")
            clone_result = clone_repository(
                fork.clone_url,
                target_dir,
                user_name=self.username,
                user_email=f"{self.username}@users.noreply.github.com"
            )

            if not clone_result["success"]:
                print(f"Failed to clone repository: {clone_result['error']}")
                return {
                    "success": False,
                    "error": f"Failed to clone repository: {clone_result['error']}",
                }

            # Add upstream remote
            repo = clone_result["repo"]
            upstream_url = f"https://github.com/{repo_full_name}.git"
            print(f"Adding upstream remote: {upstream_url}")
            add_remote_result = add_remote(repo, "upstream", upstream_url)
            if not add_remote_result["success"]:
                print(f"Failed to add upstream remote: {add_remote_result['error']}")
                return {
                    "success": False,
                    "error": f"Failed to add upstream remote: {add_remote_result['error']}",
                }

            return {
                "success": True,
                "fork_url": fork.clone_url,
                "fork_full_name": fork.full_name,
                "repo": repo,
            }
        except GithubException as e:
            print(f"GitHub API error: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def create_pull_request(
        self,
        repo_full_name: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        validate_template: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a pull request.

        Args:
            repo_full_name (str): Full name of the repository (e.g. "owner/repo")
            title (str): Title of the pull request
            body (str): Description/body of the pull request
            head (str): The name of the branch where your changes are implemented
            base (str): The name of the branch you want your changes pulled into
            validate_template (bool): Whether to validate the PR description against the template

        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation succeeded
                - pr_url (str): URL of the pull request if successful
                - error (str): Error message if unsuccessful
                - template_errors (list): List of template validation errors if any
        """
        try:
            if validate_template:
                print("Validating PR description against template...")
                validation = validate_pr_description(body)
                if not validation["valid"]:
                    print(
                        f"PR description validation failed with errors: {validation['errors']}"
                    )
                    return {
                        "success": False,
                        "error": "PR description does not match template",
                        "template_errors": validation["errors"],
                    }
                print("PR description validation passed")

            print(f"Getting repository: {repo_full_name}")
            repo = self.gh.get_repo(repo_full_name)
            print(f"Creating pull request in repository: {repo.full_name}")
            print(f"PR details: title='{title}', head='{head}', base='{base}'")
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base,
            )
            print(f"Pull request created: {pr.html_url}")
            return {"success": True, "pr_url": pr.html_url}
        except GithubException as e:
            print(f"GitHub API error: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def sync_fork(
        self, repo: Repo, branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Sync a fork with its upstream repository.

        Args:
            repo (Repo): GitPython Repo instance
            branch (str): Branch to sync (default: main)

        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation succeeded
                - error (str): Error message if unsuccessful
        """
        try:
            print(f"Syncing fork with upstream, branch: {branch}")

            # Fetch from upstream
            fetch_result = fetch_remote(repo, "upstream")
            if not fetch_result["success"]:
                return fetch_result

            # Pull from upstream
            pull_result = pull_remote(repo, "upstream", branch)
            if not pull_result["success"]:
                return pull_result

            # Push to origin
            push_result = push_remote(repo, "origin", branch)
            if not push_result["success"]:
                return push_result

            print("Successfully synced fork with upstream")
            return {"success": True}
        except Exception as e:
            error_msg = f"Unexpected error while syncing fork: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}

    def check_fork_exists(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """Check if fork exists using GitHub API."""
        try:
            response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo_name}",
                headers={"Authorization": f"token {self.token}"},
            )
            if response.status_code != 200:
                return {"success": False, "error": "Repository not found"}
            return {"success": True, "exists": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
