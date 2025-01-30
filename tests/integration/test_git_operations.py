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


def test_git_operations(setup_environment, tmp_path):
    """Test Git operations tools."""
    client = setup_environment
    os.chdir(tmp_path)

    # Initialize repository
    message = client.send_message(
        "Can you initialize a new Git repository in the current directory?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "init_repository"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Create and add a file
    with open("test.txt", "w") as f:
        f.write("test content")

    message = client.send_message(
        "Can you stage the test.txt file for commit?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "stage_files"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Create a commit
    message = client.send_message(
        "Can you create a commit with the message 'Initial commit'?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "create_commit"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Create a branch
    message = client.send_message(
        "Can you create a new branch called 'feature'?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "create_branch"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Switch to the new branch
    message = client.send_message(
        "Can you switch to the 'feature' branch?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "checkout_branch"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Get current branch
    message = client.send_message(
        "What branch are we currently on?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "get_current_branch"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["branch"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # List branches
    message = client.send_message(
        "Can you list all branches in the repository?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "list_branches"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="\n".join(result["branches"]),
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Add remote
    message = client.send_message(
        "Can you add a remote called 'origin' with URL 'https://github.com/test/test.git'?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "add_remote"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Fetch from remote
    message = client.send_message(
        "Can you fetch from the remote repository?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "fetch_remote"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Push to remote
    message = client.send_message(
        "Can you push the current branch to the remote repository?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "push_remote"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)


def test_init_repository(setup_environment, tmp_path):
    """Test the init_repository tool."""
    client = setup_environment
    repo_path = tmp_path / "new_repo"

    message = client.send_message(
        f"Can you initialize a new git repository at {repo_path}?",
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
    assert (repo_path / ".git").exists()
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )
    assert "success" in response_text.lower()


def test_clone_repository(setup_environment, test_repo, tmp_path):
    """Test the clone_repository tool."""
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
    """Test the get_current_branch tool."""
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
    """Test the create_branch tool."""
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
    """Test the checkout_branch tool."""
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
    """Test the make_commit tool."""
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
    """Test the list_branches tool."""
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


def test_add_remote(setup_environment, test_repo, tmp_path):
    """Test the add_remote tool."""
    client = setup_environment

    # Create another repo to use as remote
    remote_path = tmp_path / "remote_repo"
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
    """Test the fetch_remote tool."""
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
    """Test the pull_remote tool."""
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
    """Test the push_remote tool."""
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
    """Test the check_for_conflicts tool."""
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
    """Test the get_conflict_info tool."""
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
    """Test the resolve_conflict tool."""
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
    """Test the create_merge_commit tool."""
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
    """Test the commit_and_push tool."""
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
    """Test the can_access_repository tool."""
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
