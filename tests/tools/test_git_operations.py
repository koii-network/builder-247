"""Tests for Git operations module."""

from pathlib import Path
import pytest
from git import Repo, GitCommandError
from src.tools.git_operations import (
    create_branch,
    checkout_branch,
    make_commit,
    get_current_branch,
    list_branches,
    init_repository,
    add_remote,
    fetch_remote,
    pull_remote,
    push_remote,
    can_access_repository,
    check_for_conflicts,
    get_conflict_info,
    resolve_conflict,
    create_merge_commit,
)


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary Git repository for testing."""
    # Use pytest's tmp_path fixture
    temp_dir = tmp_path

    try:
        # Initialize Git repo
        result = init_repository(
            str(temp_dir), user_name="Test User", user_email="test@example.com"
        )
        assert result["success"]

        # Create and commit a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Initial content")

        result = make_commit(str(temp_dir), "Initial commit")
        assert result["success"]

        # Get the initial branch name
        branch_result = get_current_branch(str(temp_dir))
        assert branch_result["success"]
        initial_branch = branch_result["output"]

        yield str(temp_dir), initial_branch
    finally:
        # Clean up is handled by pytest's tmp_path
        pass


def test_create_and_checkout_branch(git_repo):
    """Test creating and checking out branches."""
    repo_path, initial_branch = git_repo

    # Create a new branch
    new_branch = "feature-branch"
    result = create_branch(repo_path, new_branch)
    assert result["success"]

    # Checkout the new branch
    result = checkout_branch(repo_path, new_branch)
    assert result["success"]

    # Verify current branch
    current = get_current_branch(repo_path)
    assert current["success"]
    assert current["output"] == new_branch


def test_make_commit(git_repo):
    """Test making a commit."""
    repo_path, _ = git_repo

    # Create a new file
    test_file = Path(repo_path) / "new_file.txt"
    test_file.write_text("New content")

    # Make a commit
    result = make_commit(repo_path, "Add new file")
    assert result["success"]

    # Verify the commit
    repo = Repo(repo_path)  # Only used for verification
    assert not repo.is_dirty()


def test_list_branches(git_repo):
    """Test listing branches."""
    repo_path, initial_branch = git_repo

    # Create some branches
    branches = ["branch1", "branch2"]
    for branch in branches:
        create_branch(repo_path, branch)

    # List branches
    result = list_branches(repo_path)
    assert result["success"]

    # Verify all branches are listed
    branch_list = result["output"]
    assert initial_branch in branch_list
    for branch in branches:
        assert branch in branch_list


def test_init_repository(tmp_path):
    """Test initializing a new Git repository."""
    result = init_repository(str(tmp_path), "Test User", "test@example.com")
    assert result["success"]

    # Verify user config
    repo = Repo(str(tmp_path))  # Only used for verification
    config = repo.config_reader()
    assert config.get_value("user", "name") == "Test User"
    assert config.get_value("user", "email") == "test@example.com"


def test_add_and_fetch_remote(tmp_path):
    """Test adding and fetching from a remote."""
    # Create a source repository that will act as our remote
    source_repo_path = tmp_path / "source_repo"
    result = init_repository(str(source_repo_path))
    assert result["success"]

    # Add some content to the source repo
    test_file = source_repo_path / "test.txt"
    test_file.write_text("Remote content")
    result = make_commit(str(source_repo_path), "Initial commit")
    assert result["success"]

    # Create our test repository
    test_repo_path = tmp_path / "test_repo"
    result = init_repository(
        str(test_repo_path), user_name="Test User", user_email="test@example.com"
    )
    assert result["success"]

    # Add the source repo as a remote
    result = add_remote(str(test_repo_path), "test-remote", str(source_repo_path))
    assert result["success"]

    # Test fetch from the remote
    result = fetch_remote(str(test_repo_path), "test-remote")
    assert result["success"]


def test_pull_and_push_remote(tmp_path):
    """Test pulling from and pushing to a remote."""
    # Create a source repository that will act as our remote - make it bare
    source_repo_path = tmp_path / "source_repo"
    Repo.init(source_repo_path, bare=True)  # We don't need to store the reference

    # Create our test repository
    test_repo_path = tmp_path / "test_repo"
    result = init_repository(
        str(test_repo_path), user_name="Test User", user_email="test@example.com"
    )
    assert result["success"]

    # Create initial content
    test_file = test_repo_path / "test.txt"
    test_file.write_text("Initial content")
    result = make_commit(str(test_repo_path), "Initial commit")
    assert result["success"]

    # Add the source repo as a remote
    result = add_remote(str(test_repo_path), "test-remote", str(source_repo_path))
    assert result["success"]

    # Get current branch name
    branch_result = get_current_branch(str(test_repo_path))
    assert branch_result["success"]
    current_branch = branch_result["output"]

    # Test push to the remote
    result = push_remote(str(test_repo_path), "test-remote", current_branch)
    assert result["success"]

    # Create a second repository to test pulling
    pull_repo_path = tmp_path / "pull_repo"
    result = init_repository(
        str(pull_repo_path), user_name="Test User", user_email="test@example.com"
    )
    assert result["success"]

    # Add the source repo as a remote to the pull repo
    result = add_remote(str(pull_repo_path), "test-remote", str(source_repo_path))
    assert result["success"]

    # Fetch first to get the remote branches
    result = fetch_remote(str(pull_repo_path), "test-remote")
    assert result["success"]

    # Create and checkout the branch
    repo = Repo(str(pull_repo_path))  # Only used for checkout
    repo.git.checkout("-b", current_branch, f"test-remote/{current_branch}")

    # Test pull from the remote
    result = pull_remote(str(pull_repo_path), "test-remote", current_branch)
    assert result["success"]

    # Verify the content was pulled
    assert (pull_repo_path / "test.txt").read_text() == "Initial content"


def test_can_access_repository():
    """Test checking repository accessibility."""
    # Test with valid public repository
    assert can_access_repository("https://github.com/torvalds/linux.git")

    # Test with invalid repository
    assert not can_access_repository(
        "https://github.com/invalid/invalid-repo-that-does-not-exist.git"
    )


def test_check_for_conflicts_and_info(git_repo):
    """Test checking for and getting info about merge conflicts."""
    repo_path, _ = git_repo

    # Create conflicting changes
    # First branch
    create_branch(repo_path, "conflict-branch1")
    test_file = Path(repo_path) / "test.txt"
    test_file.write_text("Line 1\nThis is branch 1 content\nLine 3")
    make_commit(repo_path, "Commit on branch 1")

    # Second branch
    checkout_branch(repo_path, "main")
    test_file.write_text("Line 1\nThis is main branch content\nLine 3")
    make_commit(repo_path, "Commit on branch 2")

    # Create merge conflict
    repo = Repo(repo_path)  # Only used for merge
    try:
        # Try to merge - this should fail with a conflict
        repo.git.merge("conflict-branch1")
    except GitCommandError:
        # The merge failed as expected, now let's verify the conflict
        # Check for conflicts
        result = check_for_conflicts(repo_path)
        assert result["success"]
        assert result["has_conflicts"]
        assert "test.txt" in result["conflicting_files"]

        # Get conflict info
        result = get_conflict_info(repo_path)
        assert result["success"]
        assert "test.txt" in result["conflicts"]


def test_resolve_conflict_and_create_merge_commit(git_repo):
    """Test resolving conflicts and creating merge commits."""
    repo_path, _ = git_repo

    # Create conflicting changes
    create_branch(repo_path, "conflict-branch1")
    test_file = Path(repo_path) / "test.txt"
    test_file.write_text("Line 1\nThis is branch 1 content\nLine 3")
    make_commit(repo_path, "Commit on branch 1")

    checkout_branch(repo_path, "main")
    test_file.write_text("Line 1\nThis is main branch content\nLine 3")
    make_commit(repo_path, "Commit on branch 2")

    # Try to merge to create conflict
    repo = Repo(repo_path)  # Only used for merge
    try:
        repo.git.merge("conflict-branch1")
    except GitCommandError:
        pass

    # Resolve conflict
    resolution = "Line 1\nResolved content\nLine 3"
    result = resolve_conflict(repo_path, "test.txt", resolution)
    assert result["success"]

    # Create merge commit
    result = create_merge_commit(repo_path, "Merge conflict resolved")
    assert result["success"]
    assert "commit_id" in result
