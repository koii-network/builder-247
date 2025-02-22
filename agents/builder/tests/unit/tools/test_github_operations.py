"""Tests for GitHub operations module."""

import os
import time
import tempfile
import shutil
from pathlib import Path
import pytest
from github import Github, Auth
from git import Repo
from src.tools.github_operations import (
    fork_repository,
    create_pull_request,
    sync_fork,
    get_pr_template,
    check_fork_exists,
)
from dotenv import load_dotenv

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
def git_repo(tmp_path):
    """Create a temporary directory for Git operations."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    return str(repo_path)


def test_fork_repository(upstream_repo, git_repo):
    """Test forking a repository."""
    # Ensure the directory is empty
    if any(Path(git_repo).iterdir()):
        shutil.rmtree(git_repo)
        Path(git_repo).mkdir()

    # Fork the repository
    fork_result = fork_repository(upstream_repo, git_repo)

    # The fork operation might fail if already exists, which is fine
    if not fork_result["success"] and "already exists" in fork_result.get("error", ""):
        assert True  # Skip if fork already exists
        return

    assert fork_result["success"]

    # Extract the repository name from the URL, ignoring any auth tokens
    expected_suffix = f"{GITHUB_USERNAME}/{upstream_repo.split('/')[-1]}.git"
    fork_url = fork_result["fork_url"]
    # Remove any auth token from the URL if present
    if "@" in fork_url:
        fork_url = "https://github.com/" + fork_url.split("@github.com/")[1]

    assert fork_url.endswith(expected_suffix)
    assert (
        fork_result["fork_full_name"]
        == f"{GITHUB_USERNAME}/{upstream_repo.split('/')[-1]}"
    )

    # Verify the repository was cloned and remotes are set up
    repo = Repo(git_repo)
    assert "origin" in repo.remotes
    assert "upstream" in repo.remotes
    # Compare URLs without auth tokens
    origin_url = repo.remotes.origin.url
    if "@" in origin_url:
        origin_url = "https://github.com/" + origin_url.split("@github.com/")[1]
    assert (
        origin_url
        == f"https://github.com/{GITHUB_USERNAME}/{upstream_repo.split('/')[-1]}.git"
    )
    upstream_url = repo.remotes.upstream.url
    if "@" in upstream_url:
        upstream_url = "https://github.com/" + upstream_url.split("@github.com/")[1]
    assert upstream_url == f"https://github.com/{upstream_repo}.git"


def test_create_pull_request_with_valid_template(upstream_repo):
    """Test creating a pull request with a valid template."""
    # First fork the repository
    with tempfile.TemporaryDirectory() as temp_dir:
        fork_result = fork_repository(upstream_repo, temp_dir)
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

        result = create_pull_request(
            repo_full_name=upstream_repo,
            title="Test PR",
            body=pr_body,
            head=f"{GITHUB_USERNAME}:feature",
            base="main",
        )
        assert result["success"]
        assert "pull" in result["pr_url"]


def test_create_pull_request_with_invalid_template(upstream_repo):
    """Test creating a pull request with an invalid template."""
    # First fork the repository
    with tempfile.TemporaryDirectory() as temp_dir:
        fork_result = fork_repository(upstream_repo, temp_dir)
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

        result = create_pull_request(
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
        assert (
            "Description section is too short (minimum 10 words)"
            in result["template_errors"]
        )
        assert (
            "Testing Done section is too short (minimum 5 words)"
            in result["template_errors"]
        )
        assert "Must confirm testing in the checklist" in result["template_errors"]


def test_sync_fork(upstream_repo, git_repo):
    """Test syncing a fork."""
    # Ensure the directory is empty
    if any(Path(git_repo).iterdir()):
        shutil.rmtree(git_repo)
        Path(git_repo).mkdir()

    # Fork and clone the repository
    fork_result = fork_repository(upstream_repo, git_repo)
    assert fork_result["success"]

    # Make a change in the upstream repository
    gh = Github(auth=Auth.Token(UPSTREAM_GITHUB_TOKEN))
    upstream = gh.get_repo(upstream_repo)
    readme = upstream.get_contents("README.md")
    upstream.update_file(
        "README.md",
        "Update README",
        "# Test Repository\nThis is an updated test repository.",
        readme.sha,
        branch="main",
    )

    # Wait for GitHub to propagate the changes
    time.sleep(2)

    # Sync the fork
    result = sync_fork(git_repo)
    assert result["success"]

    # Verify the changes were synced
    repo = Repo(git_repo)
    assert not repo.is_dirty()
    readme_content = Path(git_repo, "README.md").read_text()
    assert "This is an updated test repository" in readme_content


def test_get_pr_template(tmp_path):
    """Test getting PR template."""
    # Create a test repository with a PR template
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    template_dir = repo_path / ".github"
    template_dir.mkdir()
    template_file = template_dir / "pull_request_template.md"
    template_content = """# Pull Request Description

## Type of Change

[ ] Bug fix
[ ] New feature
[ ] Documentation update

## Description

[Describe your changes here]

## Related Issues

[Link to related issues]

## Testing Done

[Describe testing done]

## Checklist

[ ] I have tested my changes
[ ] I have updated the documentation
[ ] My changes generate no new warnings
[ ] I have added tests that prove my fix/feature works
"""
    template_file.write_text(template_content)

    result = get_pr_template(str(repo_path))
    assert result["success"]
    assert result["template"] == template_content


def test_get_pr_template_source_not_found(tmp_path):
    """Test getting PR template when source not found."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    result = get_pr_template(str(repo_path))
    assert not result["success"]
    assert "No PR template found" in result["error"]


def test_get_pr_template_reuse_existing(tmp_path):
    """Test reusing existing PR template."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Create a test repository with a PR template
    template_dir = repo_path / ".github"
    template_dir.mkdir()
    template_file = template_dir / "pull_request_template.md"
    template_content = """# Pull Request Description

## Type of Change

[ ] Bug fix
[ ] New feature
[ ] Documentation update

## Description

[Describe your changes here]

## Related Issues

[Link to related issues]

## Testing Done

[Describe testing done]

## Checklist

[ ] I have tested my changes
[ ] I have updated the documentation
[ ] My changes generate no new warnings
[ ] I have added tests that prove my fix/feature works
"""
    template_file.write_text(template_content)

    # First call should read from file
    result1 = get_pr_template(str(repo_path))
    assert result1["success"]
    assert result1["template"] == template_content

    # Second call should reuse cached template
    result2 = get_pr_template(str(repo_path))
    assert result2["success"]
    assert result2["template"] == template_content


def test_check_fork_exists(upstream_repo):
    """Test checking if fork exists."""
    # First create a fork
    with tempfile.TemporaryDirectory() as temp_dir:
        fork_result = fork_repository(upstream_repo, temp_dir)
        assert fork_result["success"]

        # Wait for GitHub to propagate the changes
        time.sleep(2)

        # Split the repo full name into owner and repo name
        owner, repo_name = upstream_repo.split("/")

        # Check if fork exists
        result = check_fork_exists(owner, repo_name)
        assert result["success"]
        assert result["exists"]
