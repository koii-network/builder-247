"""Integration tests for Git operations tools."""

import os
import time
import pytest
from dotenv import load_dotenv
from src.anthropic_client import AnthropicClient
from anthropic.types import Message
from git import Repo
from pathlib import Path


def get_api_key(max_retries=3, retry_delay=1):
    """
    Get API key with retries to handle mounted volume synchronization.

    Args:
        max_retries (int): Maximum number of retries
        retry_delay (int): Delay in seconds between retries
    """
    for attempt in range(max_retries):
        # Try environment variable first
        api_key = os.environ.get("CLAUDE_API_KEY")
        if api_key:
            return api_key

        # Try loading from .env
        load_dotenv()
        api_key = os.environ.get("CLAUDE_API_KEY")
        if api_key:
            return api_key

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    return None


@pytest.fixture(autouse=True)
def setup_environment(tmp_path):
    """Set up environment variables and client before each test."""
    api_key = get_api_key()
    if not api_key:
        pytest.skip("CLAUDE_API_KEY environment variable not set after retries")
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

    # Initialize git repo with proper configuration
    repo = Repo.init(repo_path)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    return repo


def normalize_repo_path(path_str: str) -> Path:
    """Normalize repository path by removing .git suffix if present and handling GitPython's string format."""
    # Handle GitPython's string representation format
    if path_str.startswith("<git.repo.base.Repo '") and path_str.endswith("'>"):
        path_str = path_str[len("<git.repo.base.Repo '") : -2]

    path = Path(path_str)
    if path.name == ".git":
        return path.parent
    return path


def test_init_repository(setup_environment, test_repo):
    """Test initializing a Git repository with proper conversation cycle."""
    client = setup_environment

    # 1. Initial prompt to Claude
    prompt = f"Can you initialize a new git repository at {test_repo.working_dir}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "init_repository"
    assert tool_use.input["path"] == str(test_repo.working_dir)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    assert (Path(test_repo.working_dir) / ".git").exists()
    response = client.send_message(
        tool_response="Repository initialized successfully at "
        + str(test_repo.working_dir),
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    final_text = response.content[0].text.lower()
    assert "repository" in final_text
    assert "initialized" in final_text


def test_clone_repository(setup_environment, test_repo, tmp_path):
    """Test cloning a Git repository with proper conversation cycle."""
    client = setup_environment
    clone_path = tmp_path / "cloned_repo"

    # 1. Initial prompt to Claude
    prompt = f"Can you clone the repository at {test_repo.working_dir} to {clone_path}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "clone_repository"
    assert tool_use.input["url"] == str(test_repo.working_dir)
    assert tool_use.input["path"] == str(clone_path)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    assert (clone_path / ".git").exists()
    assert (clone_path / "test.txt").exists()
    response = client.send_message(
        tool_response=f"Repository cloned successfully from {test_repo.working_dir} to {clone_path}",
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    final_text = response.content[0].text.lower()
    assert "repository" in final_text
    assert "cloned" in final_text


def test_get_current_branch(setup_environment, test_repo):
    """Test getting the current branch with proper conversation cycle."""
    client = setup_environment

    # 1. Initial prompt to Claude
    prompt = f"What's the current branch in the repository at {test_repo.working_dir}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "get_current_branch"
    assert tool_use.input["repo_path"] == str(test_repo.working_dir)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    assert result["output"] in ["main", "master"]  # Git may use either as default
    response = client.send_message(
        tool_response=f"Current branch is {result['output']}",
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    final_text = response.content[0].text.lower()
    assert "branch" in final_text
    assert any(name in final_text for name in ["main", "master"])


def test_create_branch(setup_environment, test_repo):
    """Test creating a new branch with proper conversation cycle."""
    client = setup_environment

    # Create feature branch for testing
    test_repo.create_head("feature")

    # 1. Initial prompt to Claude
    prompt = f"Can you create a new branch called 'feature' in the repository at {test_repo.working_dir}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "create_branch"
    assert tool_use.input["repo_path"] == str(test_repo.working_dir)
    assert tool_use.input["branch_name"] == "feature"

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    # Verify branch exists
    assert "feature" in [head.name for head in test_repo.heads]
    response = client.send_message(
        tool_response=f"Created new branch 'feature' in repository at {test_repo.working_dir}",
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    final_text = response.content[0].text.lower()
    assert "branch" in final_text
    assert "feature" in final_text
    assert "created" in final_text


def test_checkout_branch(setup_environment, test_repo):
    """Test checking out a branch with proper conversation cycle."""
    client = setup_environment

    # Create and checkout feature branch
    feature_branch = test_repo.create_head("feature")
    feature_branch.checkout()

    # Switch back to master branch
    master = test_repo.heads["master"]
    master.checkout()

    # 1. Initial prompt to Claude
    prompt = f"Can you switch to the 'feature' branch in the repository at {test_repo.working_dir}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "checkout_branch"
    assert tool_use.input["repo_path"] == str(test_repo.working_dir)
    assert tool_use.input["branch_name"] == "feature"

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    if not result["success"]:
        print(
            f"Checkout failed: {result.get('error', 'No error message')}"
        )  # Debug output
        print("Current branches:")
        for head in test_repo.heads:
            print(f"- {head.name}")
    assert result["success"]

    # Verify current branch is feature
    assert test_repo.active_branch.name == "feature"

    response = client.send_message(
        tool_response=f"Switched to branch 'feature' in repository at {test_repo.working_dir}",
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    final_text = response.content[0].text.lower()
    assert "branch" in final_text
    assert "feature" in final_text
    # Check for any indication of branch change (switch/change/move)
    assert any(word in final_text for word in ["switch", "chang", "mov", "check"])


def test_make_commit(setup_environment, test_repo):
    """Test making a commit with proper conversation cycle."""
    client = setup_environment

    # Create a new file to commit
    new_file = Path(test_repo.working_dir) / "new_file.txt"
    new_file.write_text("New content")

    # 1. Initial prompt to Claude
    prompt = f"Please commit the new file in the repository at {test_repo.working_dir} with the message 'Add new file'"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "make_commit"
    assert tool_use.input["repo_path"] == str(test_repo.working_dir)
    assert tool_use.input["message"] == "Add new file"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    # Verify file was committed
    status = os.popen(f"cd {test_repo} && git status --porcelain").read()
    assert not status  # Empty status means no uncommitted changes


def test_list_branches(setup_environment, test_repo):
    """Test listing branches with proper conversation cycle."""
    client = setup_environment

    # Create feature and develop branches
    test_repo.create_head("feature")
    test_repo.create_head("develop")

    # 1. Initial prompt to Claude
    prompt = f"Can you list all branches in the repository at {test_repo.working_dir}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "list_branches"
    assert tool_use.input["repo_path"] == str(test_repo.working_dir)

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    assert "feature" in result["output"]
    assert "develop" in result["output"]
    assert any(branch in result["output"] for branch in ["main", "master"])

    # 4. Verify Claude's response
    response = client.send_message(
        tool_response=f"The repository has the following branches: {', '.join(result['output'])}",
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    final_text = response.content[0].text.lower()
    assert "branch" in final_text
    assert "feature" in final_text
    assert "develop" in final_text


def test_add_remote(setup_environment, test_repo):
    """Test adding a remote with proper conversation cycle."""
    client = setup_environment

    # Create a bare repository to serve as remote
    remote_path = Path(test_repo.working_dir) / "remote_repo.git"
    remote_repo = Repo.init(remote_path, bare=True)

    # 1. Initial prompt to Claude
    prompt = f"Can you add a remote called 'upstream' pointing to {remote_path} in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "add_remote"
    assert normalize_repo_path(tool_use.input["repo_path"]) == normalize_repo_path(
        str(test_repo)
    )
    assert tool_use.input["name"] == "upstream"
    assert tool_use.input["url"] == str(remote_path)

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    # Verify remote was added
    remotes = [remote.name for remote in test_repo.remotes]
    assert "upstream" in remotes
    assert str(remote_path) in [remote.url for remote in test_repo.remotes]
    # Verify remote repo exists and is bare
    assert remote_repo.bare


def test_fetch_remote(setup_environment, test_repo):
    """Test fetching from a remote with proper conversation cycle."""
    client = setup_environment

    # Create a bare repository to serve as remote and add it
    remote_path = Path(test_repo.working_dir) / "remote_repo.git"
    Repo.init(remote_path, bare=True)
    test_repo.create_remote("origin", str(remote_path))

    # 1. Initial prompt to Claude
    prompt = f"Can you fetch from the 'origin' remote in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "fetch_remote"
    assert normalize_repo_path(tool_use.input["repo_path"]) == normalize_repo_path(
        str(test_repo)
    )
    assert tool_use.input["remote_name"] == "origin"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]


def test_pull_remote(setup_environment, test_repo):
    """Test pulling from a remote with proper conversation cycle."""
    client = setup_environment

    # Create a bare repository to serve as remote and add it
    remote_path = Path(test_repo.working_dir) / "remote_repo.git"
    Repo.init(remote_path, bare=True)
    test_repo.create_remote("origin", str(remote_path))

    # Push initial branch to set up tracking
    test_repo.git.push("--set-upstream", "origin", test_repo.active_branch.name)

    # Make a change in the remote
    clone_path = Path(test_repo.working_dir) / "temp_clone"
    clone_repo = Repo.clone_from(str(remote_path), str(clone_path))
    test_file = clone_path / "test.txt"
    test_file.write_text("Updated in remote")
    clone_repo.index.add([str(test_file)])
    clone_repo.index.commit("Update in remote")
    clone_repo.git.push()

    # 1. Initial prompt to Claude
    prompt = f"Can you pull from the 'origin' remote in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "pull_remote"
    assert normalize_repo_path(tool_use.input["repo_path"]) == normalize_repo_path(
        str(test_repo)
    )
    # remote_name is optional since it has a default value of "origin"
    if "remote_name" in tool_use.input:
        assert tool_use.input["remote_name"] == "origin"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]

    # 4. Verify Claude's final response
    response = client.send_message(
        tool_response=f"Successfully pulled changes from origin in repository at {test_repo}",
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    final_text = response.content[0].text.lower()
    assert "pull" in final_text
    assert "success" in final_text or "complete" in final_text


def test_push_remote(setup_environment, test_repo):
    """Test pushing to a remote with proper conversation cycle."""
    client = setup_environment

    # Create a bare repository to serve as remote and add it
    remote_path = Path(test_repo.working_dir) / "remote_repo.git"
    Repo.init(remote_path, bare=True)
    test_repo.create_remote("origin", str(remote_path))

    # Make a change to push
    test_file = Path(test_repo.working_dir) / "test.txt"
    test_file.write_text("Updated content")
    test_repo.index.add([str(test_file)])
    test_repo.index.commit("Update for push test")

    # 1. Initial prompt to Claude
    prompt = f"Can you push to the 'origin' remote in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "push_remote"
    assert normalize_repo_path(tool_use.input["repo_path"]) == normalize_repo_path(
        str(test_repo)
    )
    # remote_name is optional since it has a default value of "origin"
    if "remote_name" in tool_use.input:
        assert tool_use.input["remote_name"] == "origin"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]

    # 4. Verify Claude's final response
    response = client.send_message(
        tool_response=f"Successfully pushed changes to origin in repository at {test_repo}",
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    final_text = response.content[0].text.lower()
    assert "push" in final_text
    assert "success" in final_text or "complete" in final_text


def test_check_for_conflicts(setup_environment, test_repo):
    """Test checking for conflicts with proper conversation cycle."""
    client = setup_environment

    # Create a conflicting situation
    test_file = Path(test_repo.working_dir) / "test.txt"
    test_file.write_text("Conflict content")
    test_repo.index.add([str(test_file)])
    test_repo.index.commit("Conflict commit")

    # 1. Initial prompt to Claude
    prompt = f"Can you check for conflicts in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "check_for_conflicts"
    assert normalize_repo_path(tool_use.input["repo_path"]) == normalize_repo_path(
        str(test_repo)
    )

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]


def test_get_conflict_info(setup_environment, test_repo):
    """Test getting conflict information with proper conversation cycle."""
    client = setup_environment

    # Create a conflicting situation
    test_file = Path(test_repo.working_dir) / "test.txt"
    test_file.write_text("Conflict content")
    test_repo.index.add([str(test_file)])
    test_repo.index.commit("Conflict commit")

    # 1. Initial prompt to Claude
    prompt = f"Can you get conflict information for the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "get_conflict_info"
    assert normalize_repo_path(tool_use.input["repo_path"]) == normalize_repo_path(
        str(test_repo)
    )

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]


def test_resolve_conflict(setup_environment, test_repo):
    """Test resolving conflicts with proper conversation cycle."""
    client = setup_environment

    # Create a conflicting situation
    test_file = Path(test_repo.working_dir) / "test.txt"
    test_file.write_text("Conflict content")
    test_repo.index.add([str(test_file)])
    test_repo.index.commit("Conflict commit")

    # 1. Initial prompt to Claude
    prompt = (
        f"Can you resolve the conflict in test.txt with content 'Resolved content' "
        f"in the repository at {test_repo}?"
    )
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "resolve_conflict"
    assert normalize_repo_path(tool_use.input["repo_path"]) == normalize_repo_path(
        str(test_repo)
    )
    assert tool_use.input["file_path"] == "test.txt"
    assert tool_use.input["resolution"] == "Resolved content"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]


def test_create_merge_commit(setup_environment, test_repo):
    """Test creating a merge commit with proper conversation cycle."""
    client = setup_environment

    # Create a situation that needs a merge commit
    test_file = Path(test_repo.working_dir) / "test.txt"
    test_file.write_text("Merge content")
    test_repo.index.add([str(test_file)])
    test_repo.index.commit("Pre-merge commit")

    # 1. Initial prompt to Claude
    prompt = f"Can you create a merge commit in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "create_merge_commit"
    assert normalize_repo_path(tool_use.input["repo_path"]) == normalize_repo_path(
        str(test_repo)
    )
    assert tool_use.input["message"] == "Merge commit"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]


def test_commit_and_push(setup_environment, test_repo):
    """Test committing and pushing changes with proper conversation cycle."""
    client = setup_environment

    # Create a change to commit and push
    test_file = Path(test_repo.working_dir) / "test.txt"
    test_file.write_text("New content for commit and push")

    # Create a bare repository to serve as remote and add it
    remote_path = Path(test_repo.working_dir) / "remote_repo.git"
    Repo.init(remote_path, bare=True)
    test_repo.create_remote("origin", str(remote_path))

    # 1. Initial prompt to Claude
    prompt = f"Can you commit and push the changes in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "commit_and_push"
    assert normalize_repo_path(tool_use.input["repo_path"]) == normalize_repo_path(
        str(test_repo)
    )
    assert "message" in tool_use.input

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]


def test_can_access_repository(setup_environment):
    """Test checking repository accessibility with proper conversation cycle."""
    client = setup_environment

    # 1. Initial prompt to Claude
    prompt = "Can you check if the repository at https://github.com/octocat/Hello-World.git is accessible?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "can_access_repository"
    assert tool_use.input["repo_url"] == "https://github.com/octocat/Hello-World.git"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert isinstance(result, bool)
    assert result is True

    # Test with non-existent repository
    prompt = "Can you check if the repository at https://github.com/octocat/non-existent-repo.git is accessible?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "can_access_repository"
    assert (
        tool_use.input["repo_url"] == "https://github.com/octocat/non-existent-repo.git"
    )

    # Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert isinstance(result, bool)
    assert result is False
