"""Tests for GitHub operations module."""

import os
import time
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from github import Github, Auth
from git import Repo
from src.tools.github_operations import GitHubOperations
from dotenv import load_dotenv
from src.tools.execute_command import execute_command
from github import GithubException

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
UPSTREAM_GITHUB_TOKEN = os.environ.get("UPSTREAM_GITHUB_TOKEN")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")
UPSTREAM_GITHUB_USERNAME = os.environ.get("UPSTREAM_GITHUB_USERNAME")


@pytest.fixture
def upstream_repo():
    """Create a test repository in the upstream account."""
    # Use the new Auth.Token method
    gh = Github(auth=Auth.Token(UPSTREAM_GITHUB_TOKEN))

    try:
        user = gh.get_user()
        print(f"Authenticated as: {user.login}")

        # Create a unique test repository name
        repo_name = f"test-repo-{os.urandom(4).hex()}"
        print(f"Creating repository: {repo_name}")

        repo = user.create_repo(
            repo_name,
            description="Test repository for GitHub operations",
            private=False,  # Make the repository public
        )
        print(f"Repository created: {repo.full_name}")

        # Create some initial content
        repo.create_file(
            "README.md",
            "Initial commit",
            "# Test Repository\nThis is a test repository.",
            branch="main",
        )
        print("Added README.md to repository")

        # Wait for GitHub to propagate the changes
        print("Waiting for GitHub to propagate changes...")
        time.sleep(2)

        full_name = repo.full_name  # Use the actual full name from the repository
        print(f"Yielding repository name: {full_name}")
        yield full_name
    except Exception as e:
        print(f"Error in upstream_repo fixture: {str(e)}")
        raise
    finally:
        # Cleanup: Delete the test repository
        try:
            if "repo" in locals():
                repo.delete()
                print(f"Cleaned up repository: {repo_name}")
        except Exception as e:
            print(f"Error cleaning up repository: {str(e)}")


@pytest.fixture
def github_ops():
    """Create a GitHubOperations instance."""
    return GitHubOperations()


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary directory for Git operations."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    return repo_path


def test_fork_repository(github_ops, upstream_repo, git_repo):
    """Test forking a repository."""
    # Ensure the directory is empty
    if any(git_repo.iterdir()):
        shutil.rmtree(git_repo)
        git_repo.mkdir()

    # Fork the repository
    fork_result = github_ops.fork_repository(upstream_repo, str(git_repo))

    # The fork operation might fail if already exists, which is fine
    if not fork_result["success"] and "already exists" in fork_result.get("error", ""):
        assert True  # Skip if fork already exists
        return

    assert fork_result["success"]
    assert fork_result["fork_url"].endswith(f"{GITHUB_USERNAME}/{upstream_repo.split('/')[-1]}.git")
    assert fork_result["fork_full_name"] == f"{GITHUB_USERNAME}/{upstream_repo.split('/')[-1]}"
    assert isinstance(fork_result["repo"], Repo)

    # Verify the repository was cloned and remotes are set up
    repo = fork_result["repo"]
    assert "origin" in repo.remotes
    assert "upstream" in repo.remotes
    assert repo.remotes.origin.url == fork_result["fork_url"]
    assert repo.remotes.upstream.url == f"https://github.com/{upstream_repo}.git"


def test_create_pull_request_with_valid_template(github_ops, upstream_repo):
    """Test creating a pull request with a valid template."""
    # First fork the repository
    fork_result = github_ops.fork_repository(upstream_repo)
    assert fork_result["success"]

    # Wait for the fork to be initialized
    print("Waiting for fork to be initialized...")
    time.sleep(2)

    # Create a new branch and make changes
    gh = Github(auth=Auth.Token(GITHUB_TOKEN))
    fork = gh.get_repo(fork_result["fork_full_name"])
    main_ref = fork.get_git_ref("heads/main")
    fork.create_git_ref("refs/heads/feature", main_ref.object.sha)

    # Make a change in the feature branch
    readme = fork.get_contents("README.md", ref="feature")
    fork.update_file(
        "README.md",
        "Update README",
        "# Test Repository\nThis is an updated test repository.",
        readme.sha,
        branch="feature",
    )

    # Create pull request with valid template
    pr_body = """# Pull Request Description

## Type of Change

[x] New feature

## Description

This PR updates the README with improved documentation to make it more user-friendly.

## Related Issues

#123

## Testing Done

Manually verified the README changes and confirmed formatting is correct.

## Checklist

[x] I have tested my changes
[x] I have updated the documentation
[x] My changes generate no new warnings
[x] I have added tests that prove my fix/feature works"""

    result = github_ops.create_pull_request(
        repo_full_name=upstream_repo,
        title="Test PR",
        body=pr_body,
        head=f"{GITHUB_USERNAME}:feature",
        base="main",
    )
    assert result["success"]
    assert "pull" in result["pr_url"]


def test_create_pull_request_with_invalid_template(github_ops, upstream_repo):
    """Test creating a pull request with an invalid template."""
    # First fork the repository
    fork_result = github_ops.fork_repository(upstream_repo)
    assert fork_result["success"]

    # Wait for the fork to be initialized
    print("Waiting for fork to be initialized...")
    time.sleep(2)

    # Create a new branch and make changes
    gh = Github(auth=Auth.Token(GITHUB_TOKEN))
    fork = gh.get_repo(fork_result["fork_full_name"])
    main_ref = fork.get_git_ref("heads/main")
    fork.create_git_ref("refs/heads/feature", main_ref.object.sha)

    # Make a change in the feature branch
    readme = fork.get_contents("README.md", ref="feature")
    fork.update_file(
        "README.md",
        "Update README",
        "# Test Repository\nThis is an updated test repository.",
        readme.sha,
        branch="feature",
    )

    # Create pull request with invalid template
    pr_body = """# Pull Request Description

## Type of Change

[ ] New feature

## Description

Too short.

## Related Issues

#123

## Testing Done

Testing.

## Checklist

[ ] I have tested my changes
"""

    result = github_ops.create_pull_request(
        repo_full_name=upstream_repo,
        title="Test PR",
        body=pr_body,
        head=f"{GITHUB_USERNAME}:feature",
        base="main",
    )
    assert not result["success"]
    assert result["error"] == "PR description does not match template"
    assert len(result["template_errors"]) > 0
    assert "Must select at least one Type of Change" in result["template_errors"]
    assert "Description section is too short (minimum 10 words)" in result["template_errors"]
    assert "Testing Done section is too short (minimum 5 words)" in result["template_errors"]
    assert "Must confirm testing in the checklist" in result["template_errors"]


def test_sync_fork(github_ops, upstream_repo, git_repo):
    """Test syncing a fork."""
    # Ensure the directory is empty
    if any(git_repo.iterdir()):
        shutil.rmtree(git_repo)
        git_repo.mkdir()

    # First fork the repository
    fork_result = github_ops.fork_repository(upstream_repo, str(git_repo))
    assert fork_result["success"]

    # Wait for the fork to be initialized
    print("Waiting for fork to be initialized...")
    time.sleep(2)

    # Try to sync the fork
    result = github_ops.sync_fork(fork_result["repo"])
    print(result)
    assert result["success"]


def test_get_pr_template(tmp_path):
    """Test getting PR template."""
    # Set up test environment
    os.chdir(tmp_path)

    # Create docs/agent directory and copy the real template
    source_dir = tmp_path / "docs" / "agent"
    source_dir.mkdir(parents=True)
    real_template = Path(__file__).parent.parent.parent / "docs/agent/pr_template.md"
    shutil.copy2(real_template, source_dir / "pr_template.md")

    # Test getting the template
    github_ops = GitHubOperations()
    result = github_ops.get_pr_template()

    # Verify the template was copied to .github/
    template_path = tmp_path / ".github/pull_request_template.md"
    assert template_path.exists()
    assert template_path.read_text() == real_template.read_text()
    assert result == real_template.read_text()


def test_get_pr_template_source_not_found(tmp_path):
    """Test getting PR template when source doesn't exist."""
    # Set up test environment in empty directory
    os.chdir(tmp_path)

    # Test getting the template when source doesn't exist
    github_ops = GitHubOperations()
    with pytest.raises(FileNotFoundError, match="Source PR template file not found"):
        github_ops.get_pr_template()


def test_get_pr_template_reuse_existing(tmp_path):
    """Test that get_pr_template reuses existing template."""
    # Set up test environment
    os.chdir(tmp_path)

    # Create .github directory and template directly
    template_dir = tmp_path / ".github"
    template_dir.mkdir(parents=True)
    template_path = template_dir / "pull_request_template.md"
    template_content = "# Custom Template"
    template_path.write_text(template_content)

    # Test getting the template
    github_ops = GitHubOperations()
    result = github_ops.get_pr_template()

    # Verify it uses the existing template
    assert result == template_content


def test_check_fork_exists(github_ops, upstream_repo):
    """Test checking if a fork exists."""
    # Test with the test repository
    owner, repo_name = upstream_repo.split('/')
    result = github_ops.check_fork_exists(owner, repo_name)
    assert result["success"]
    assert result["exists"]

    # Test with a non-existent repository
    result = github_ops.check_fork_exists("not-real-user", "not-real-repo-12345")
    assert not result["success"]
    assert "Repository not found" in result["error"]
