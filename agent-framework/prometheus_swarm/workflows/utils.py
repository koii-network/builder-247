"""Centralized workflow utilities."""

import os
import shutil
from github import Github
from git import Repo
from prometheus_swarm.utils.logging import log_key_value, log_error
from prometheus_swarm.tools.file_operations.implementations import list_files
from prometheus_swarm.tools.github_operations.parser import extract_section
from prometheus_swarm.utils.signatures import verify_and_parse_signature
from typing import Optional, Tuple


def get_fork_name(
    source_owner: str, source_repo_url: str, github_token: str | None = None
) -> str:
    """Generate a unique fork name based on the upstream repo name and source owner.

    Args:
        source_owner: The owner of the source fork (where we're getting PRs from)
        source_repo_url: The URL of the source repository (can be fork or upstream)
        github_token: Optional GitHub token for authentication

    Returns:
        str: The unique fork name in the format {upstream_repo_name}-{source_owner}
    """
    # Set up GitHub client
    if isinstance(github_token, str):
        gh = Github(github_token)
    elif isinstance(github_token, Github):
        gh = github_token
    else:
        raise ValueError("GitHub token is required")

    # Extract owner/repo from URL
    parts = source_repo_url.strip("/").split("/")
    repo_owner, repo_name = parts[-2:]

    # Get the source repo
    source_repo = gh.get_repo(f"{repo_owner}/{repo_name}")

    # Get the upstream repo name:
    # If source_repo is a fork, get name from its parent (upstream)
    # If source_repo is the upstream itself, use its own name
    # Either way, we get the upstream repo name
    upstream_name = source_repo.parent.name if source_repo.fork else source_repo.name

    # Create fork name using upstream name and source owner
    return f"{upstream_name}-{source_owner}"


def check_required_env_vars(env_vars: list[str]):
    """Check if all required environment variables are set."""
    missing_vars = [var for var in env_vars if not os.environ.get(var)]

    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please ensure these are set in your .env file or environment."
        )


def validate_github_auth(github_token: str, github_username: str):
    """Validate GitHub authentication."""
    try:
        gh = Github(github_token)
        user = gh.get_user()
        username = user.login
        if username != github_username:
            raise ValueError(
                f"GitHub token belongs to {username}, but GITHUB_USERNAME is set to {github_username}"
            )
        log_key_value("Successfully authenticated as", username)
    except Exception as e:
        log_error(e, "GitHub authentication failed")
        raise RuntimeError(str(e))


def _setup_git_user_config(repo: Repo, github_username: str):
    """Configure Git user info for the repository.

    Args:
        repo: GitPython Repo instance
        github_username: GitHub username to configure
    """
    with repo.config_writer() as config:
        config.set_value("user", "name", github_username)
        config.set_value(
            "user",
            "email",
            f"{github_username}@users.noreply.github.com",
        )


def setup_repository(
    repo_url: str,
    github_token: str = None,
    github_username: str = None,
    skip_fork: bool = False,
    branch: str = None,
) -> dict:
    """Set up a repository by cloning and configuring it.

    Args:
        repo_url: URL of the repository (e.g., https://github.com/owner/repo)
        github_token: Optional GitHub token for authentication
        github_username: Optional GitHub username for Git config
        skip_fork: Optional flag to skip forking and clone directly
        branch: Optional branch to clone (defaults to repository's default branch)

    Returns:
        dict: Result with success status, repository details, and paths
    """
    try:
        # Extract owner/repo from URL
        parts = repo_url.strip("/").split("/")
        repo_owner, repo_name = parts[-2:]
        repo_full_name = f"{repo_owner}/{repo_name}"

        # Fork the repository if needed
        if not skip_fork:
            fork_result = _fork_repository(repo_full_name, github_token)
            if not fork_result["success"]:
                raise Exception(fork_result.get("error", "Failed to fork repository"))
            clone_url = fork_result["data"]["fork_url"]
            fork_owner = fork_result["data"]["owner"]
            fork_name = fork_result["data"]["repo"]
        else:
            clone_url = repo_url
            fork_owner = repo_owner
            fork_name = repo_name

        # Generate sequential repo path
        base_dir = os.path.abspath("./repos")
        os.makedirs(base_dir, exist_ok=True)

        counter = 0
        while True:
            candidate_path = os.path.join(base_dir, f"repo_{counter}")
            if not os.path.exists(candidate_path):
                repo_path = candidate_path
                break
            counter += 1

        # Clean existing repository
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)

        # Create parent directory
        os.makedirs(os.path.dirname(repo_path), exist_ok=True)

        # Save original directory
        original_dir = os.getcwd()

        # Add GitHub token to URL for authentication
        if github_token and "github.com" in clone_url:
            auth_url = clone_url.replace("https://", f"https://{github_token}@")
        else:
            auth_url = clone_url

        # Clone the repository
        log_key_value("Cloning repository", clone_url)
        log_key_value("Clone path", repo_path)

        # Clone specific branch if provided, otherwise clone default branch
        if branch:
            repo = Repo.clone_from(auth_url, repo_path, branch=branch)
        else:
            repo = Repo.clone_from(auth_url, repo_path)

        # Configure Git user info if username provided
        if github_username:
            _setup_git_user_config(repo, github_username)

        # Add upstream remote if this is a fork
        if not skip_fork:
            repo.create_remote("upstream", repo_url)

        return {
            "success": True,
            "message": "Successfully set up repository",
            "data": {
                "clone_path": repo_path,
                "original_dir": original_dir,
                "repo": repo,
                "fork_url": clone_url,
                "fork_owner": fork_owner,
                "fork_name": fork_name,
            },
        }

    except Exception as e:
        error_msg = str(e)
        log_error(e, "Repository setup failed")
        return {
            "success": False,
            "message": "Failed to set up repository",
            "data": None,
            "error": error_msg,
        }


def cleanup_repository(original_dir: str, repo_path: str):
    """Clean up repository directory and return to original directory.

    Args:
        original_dir: Original directory to return to
        repo_path: Repository path to clean up
    """
    os.chdir(original_dir)
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)


def get_current_files():
    """Get current files in repository."""
    files_result = list_files(".")
    if not files_result["success"]:
        raise Exception(f"Failed to get file list: {files_result['message']}")

    return files_result["data"]["files"]


def _fork_repository(
    repo_full_name: str,
    github_token: Optional[str] = None,
    fork_name: Optional[str] = None,
) -> dict:
    """Fork a repository.

    Args:
        repo_full_name: Full name of repository (owner/repo)
        github_token: Optional GitHub token to use. Defaults to GITHUB_TOKEN env var.
        fork_name: Optional custom name for the fork. If not provided, uses the original repo name.

    Returns:
        dict: Result with success status and fork URL if successful
    """
    try:
        if fork_name:
            log_key_value("Custom fork name", fork_name)
        token = github_token or os.environ["GITHUB_TOKEN"]
        gh = Github(token)
        source_repo = gh.get_repo(repo_full_name)

        # Get authenticated user
        user = gh.get_user()
        username = user.login

        # Use provided fork name or original repo name
        repo_name = fork_name or source_repo.name

        # Check if fork already exists
        try:
            fork = gh.get_repo(f"{username}/{repo_name}")
            log_key_value("Using existing fork", fork.html_url)
        except Exception:
            # Create fork if it doesn't exist
            fork = user.create_fork(source_repo, name=repo_name)
            log_key_value("Created new fork", fork.html_url)

        # Wait for fork to be ready
        log_key_value("Waiting for fork to be ready", "")
        max_retries = 10
        for _ in range(max_retries):
            try:
                fork.get_commits().get_page(0)
                break
            except Exception:
                import time

                time.sleep(1)

        return {
            "success": True,
            "message": f"Successfully forked {repo_full_name}",
            "data": {
                "fork_url": fork.html_url,
                "owner": username,
                "repo": repo_name,
            },
        }

    except Exception as e:
        error_msg = str(e)
        log_error(e, "Fork failed")
        return {
            "success": False,
            "message": "Failed to fork repository",
            "data": None,
            "error": error_msg,
        }


def extract_pr_signature(
    pr_body: str, section_name: str = "STAKING_KEY"
) -> Tuple[Optional[str], Optional[str]]:
    """Extract staking key and signature from a PR description.

    Args:
        pr_body: The PR description text
        section_name: Name of the section containing the signature (default: STAKING_KEY)

    Returns:
        Tuple[Optional[str], Optional[str]]: (staking_key, signature) or (None, None) if not found
    """
    signature_section = extract_section(pr_body, section_name)
    if not signature_section:
        return None, None

    parts = signature_section.strip().split(":")
    if len(parts) != 2:
        return None, None

    return parts[0].strip(), parts[1].strip()


def verify_pr_signatures(
    pr_body: str,
    task_id: str,
    round_number: int,
    expected_staking_key: str = None,
    expected_action: str = None,
) -> bool:
    """Verify signatures in a PR description.

    Args:
        pr_body: PR description text
        task_id: Expected task ID
        round_number: Expected round number
        expected_staking_key: Optional expected staking key
        expected_action: Optional expected action type (e.g. "task", "merge", "audit")

    Returns:
        bool: True if signatures are valid
    """
    # Extract signatures using parser
    staking_signature_section = extract_section(pr_body, "STAKING_KEY")

    if not staking_signature_section:
        print("Missing staking key signature")
        return False

    # Parse the signature sections to get the specific staking key's signatures
    staking_parts = staking_signature_section.strip().split(":")

    if len(staking_parts) != 2:
        print("Invalid staking signature format")
        return False

    staking_key = staking_parts[0].strip()
    staking_signature = staking_parts[1].strip()

    # If expected staking key provided, verify it matches
    if expected_staking_key and staking_key != expected_staking_key:
        print(f"Staking key mismatch: {staking_key} != {expected_staking_key}")
        return False

    # Verify signature and validate payload
    expected_values = {
        "taskId": task_id,
        "roundNumber": round_number,
        "stakingKey": staking_key,
    }
    if expected_action:
        expected_values["action"] = expected_action

    result = verify_and_parse_signature(staking_signature, staking_key, expected_values)

    if result.get("error"):
        print(f"Invalid signature: {result['error']}")
        return False

    return True


def create_remote_branch(
    repo_owner: str,
    repo_name: str,
    branch_name: str,
    base_branch: str = "main",
    github_token: Optional[str] = None,
) -> dict:
    """Create a branch on a GitHub repository.

    Args:
        repo_owner: Owner of the repository
        repo_name: Name of the repository
        branch_name: Name of the branch to create
        base_branch: Base branch to create from (default: main)
        github_token: Optional GitHub token to use. Defaults to GITHUB_TOKEN env var.

    Returns:
        dict: Result with success status and branch info if successful
    """
    try:
        token = github_token or os.environ["GITHUB_TOKEN"]
        gh = Github(token)
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")

        # Get the base branch's latest commit
        base = repo.get_branch(base_branch)
        base_sha = base.commit.sha

        # Create the new branch
        ref = f"refs/heads/{branch_name}"
        repo.create_git_ref(ref=ref, sha=base_sha)

        return {
            "success": True,
            "message": f"Successfully created branch {branch_name}",
            "data": {
                "branch_name": branch_name,
                "base_branch": base_branch,
                "base_sha": base_sha,
            },
        }

    except Exception as e:
        error_msg = str(e)
        log_error(e, "Branch creation failed")
        return {
            "success": False,
            "message": "Failed to create branch",
            "data": None,
            "error": error_msg,
        }
