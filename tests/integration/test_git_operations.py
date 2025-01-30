"""Integration tests for Git operations tools."""

import os
import pytest
from dotenv import load_dotenv
from src.anthropic_client import AnthropicClient
from anthropic.types import Message

# Load environment variables before any tests
load_dotenv()


@pytest.fixture(autouse=True)
def setup_environment(tmp_path):
    """Set up environment variables and client before each test."""
    api_key = os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        pytest.skip("CLAUDE_API_KEY environment variable not set")
    temp_db = tmp_path / "test.db"
    client = AnthropicClient(api_key=api_key, db_path=temp_db)
    client.register_tools_from_directory("src/tools/definitions/git_operations")
    return client


@pytest.fixture
def test_repo(tmp_path):
    """Create a test git repository."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Create a test file
    test_file = repo_path / "test.txt"
    test_file.write_text("Hello, world!")

    # Initialize git repo
    os.system(
        f"cd {repo_path} && git init && git add . && git commit -m 'Initial commit'"
    )

    return repo_path


def test_init_repository(setup_environment, tmp_path):
    """Test initializing a Git repository."""
    client = setup_environment

    message = client.send_message(
        f"Can you initialize a new git repository at {tmp_path}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "init_repository"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The repository was initialized successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    assert (tmp_path / ".git").exists()
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_clone_repository(setup_environment, test_repo, tmp_path):
    """Test cloning a Git repository."""
    client = setup_environment
    clone_path = tmp_path / "cloned_repo"

    message = client.send_message(
        f"Can you clone the repository at {test_repo} to {clone_path}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "clone_repository"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The repository was cloned successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    assert (clone_path / ".git").exists()
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_get_current_branch(setup_environment, test_repo):
    """Test getting the current branch."""
    client = setup_environment

    message = client.send_message(
        f"What's the current branch in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "get_current_branch"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            f"The current branch is {result['output']}"
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "main" in response_text.lower() or "master" in response_text.lower()


def test_create_branch(setup_environment, test_repo):
    """Test creating a new branch."""
    client = setup_environment

    message = client.send_message(
        f"Can you create a new branch called 'feature' in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "create_branch"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The branch was created successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_checkout_branch(setup_environment, test_repo):
    """Test checking out a branch."""
    client = setup_environment

    # First create a branch to checkout
    os.system(f"cd {test_repo} && git branch feature")

    message = client.send_message(
        f"Can you switch to the 'feature' branch in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "checkout_branch"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The branch was checked out successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_make_commit(setup_environment, test_repo):
    """Test making a commit."""
    client = setup_environment

    # Create a new file to commit
    test_file = test_repo / "new_file.txt"
    test_file.write_text("New content")

    message = client.send_message(
        f"Can you commit the new file in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "make_commit"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The changes were committed successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_list_branches(setup_environment, test_repo):
    """Test listing branches."""
    client = setup_environment

    # Create some branches to list
    os.system(f"cd {test_repo} && git branch feature && git branch develop")

    message = client.send_message(
        f"Can you list all branches in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "list_branches"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            f"Here are the branches:\n{result['output']}"
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "feature" in response_text.lower()
    assert "develop" in response_text.lower()


def test_add_remote(setup_environment, test_repo):
    """Test adding a remote."""
    client = setup_environment

    # Create another repo to use as remote
    remote_path = test_repo / "remote_repo"
    os.system(f"git init {remote_path}")

    message = client.send_message(
        f"Can you add a remote called 'upstream' pointing to {remote_path} in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "add_remote"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        "The remote was added successfully." if result["success"] else result["error"],
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_fetch_remote(setup_environment, test_repo):
    """Test fetching from a remote."""
    client = setup_environment

    # Add a remote to fetch from
    os.system(
        f"cd {test_repo} && git remote add origin https://github.com/octocat/Hello-World.git"
    )

    message = client.send_message(
        f"Can you fetch from the 'origin' remote in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "fetch_remote"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The remote was fetched successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_pull_remote(setup_environment, test_repo):
    """Test pulling from a remote."""
    client = setup_environment

    # Add a remote to pull from
    os.system(
        f"cd {test_repo} && git remote add origin https://github.com/octocat/Hello-World.git"
    )

    message = client.send_message(
        f"Can you pull from the 'origin' remote in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "pull_remote"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        "The remote was pulled successfully." if result["success"] else result["error"],
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_push_remote(setup_environment, test_repo):
    """Test pushing to a remote."""
    client = setup_environment

    # Add a remote to push to
    os.system(
        f"cd {test_repo} && git remote add origin https://github.com/octocat/Hello-World.git"
    )

    message = client.send_message(
        f"Can you push to the 'origin' remote in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "push_remote"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The changes were pushed successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_check_for_conflicts(setup_environment, test_repo):
    """Test checking for conflicts."""
    client = setup_environment

    # Create a conflict situation
    test_file = test_repo / "test.txt"
    test_file.write_text("Conflicting content")
    os.system(f"cd {test_repo} && git add . && git commit -m 'Create conflict'")

    message = client.send_message(
        f"Can you check for any merge conflicts in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "check_for_conflicts"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        "Checked for conflicts." if result["success"] else result["error"],
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "conflict" in response_text.lower()


def test_get_conflict_info(setup_environment, test_repo):
    """Test getting conflict information."""
    client = setup_environment

    # Create a conflict situation
    test_file = test_repo / "test.txt"
    test_file.write_text("Conflicting content")
    os.system(f"cd {test_repo} && git add . && git commit -m 'Create conflict'")

    message = client.send_message(
        f"Can you get information about any conflicts in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "get_conflict_info"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            f"Here are the conflicts:\n{result['conflicts']}"
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "conflict" in response_text.lower()


def test_resolve_conflict(setup_environment, test_repo):
    """Test resolving a conflict."""
    client = setup_environment

    # Create a conflict situation
    test_file = test_repo / "test.txt"
    test_file.write_text("Conflicting content")
    os.system(f"cd {test_repo} && git add . && git commit -m 'Create conflict'")

    message = client.send_message(
        f"Can you resolve the conflict in 'test.txt' in the repository at {test_repo} by keeping the current version?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "resolve_conflict"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The conflict was resolved successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_create_merge_commit(setup_environment, test_repo):
    """Test creating a merge commit."""
    client = setup_environment

    # Set up a merge situation
    os.system(
        f"""
        cd {test_repo} &&
        git checkout -b feature &&
        echo "Feature change" > feature.txt &&
        git add . &&
        git commit -m "Feature commit" &&
        git checkout main &&
        echo "Main change" > main.txt &&
        git add . &&
        git commit -m "Main commit"
    """
    )

    message = client.send_message(
        f"Can you create a merge commit in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "create_merge_commit"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The merge commit was created successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_commit_and_push(setup_environment, test_repo):
    """Test committing and pushing changes."""
    client = setup_environment

    # Create changes to commit and push
    test_file = test_repo / "new_file.txt"
    test_file.write_text("New content")
    os.system(
        f"cd {test_repo} && git remote add origin https://github.com/octocat/Hello-World.git"
    )

    message = client.send_message(
        f"Can you commit and push all changes in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "commit_and_push"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "The changes were committed and pushed successfully."
            if result["success"]
            else result["error"]
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_can_access_repository(setup_environment):
    """Test checking repository accessibility."""
    client = setup_environment

    message = client.send_message(
        "Can you check if we can access the Linux kernel repository?",
        tool_choice={"type": "any"},
    )
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = [block for block in message.content if block.type == "tool_use"][0]
    assert tool_use.name == "can_access_repository"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        (
            "Yes, we can access the repository."
            if result["success"]
            else "No, we cannot access the repository."
        ),
        tool_choice={"type": "auto"},
    )
    assert isinstance(response, Message)
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "access" in response_text.lower()
