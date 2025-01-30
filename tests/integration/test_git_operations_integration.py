"""Integration tests for Git operations tools."""

import os
import pytest
from dotenv import load_dotenv
from src.anthropic_client import AnthropicClient
from anthropic.types import Message
from git import Repo
from git.exc import GitCommandError

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
    """Test initializing a Git repository with proper conversation cycle."""
    client = setup_environment
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()

    # 1. Initial prompt to Claude
    prompt = f"Can you initialize a new git repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "init_repository"
    assert tool_use.input["path"] == str(test_repo)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    assert (test_repo / ".git").exists()
    response = client.send_message(
        tool_response="Repository initialized successfully at " + str(test_repo),
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

    # Create a test file and commit it
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")
    os.system(
        f"cd {test_repo} && git init && git add . && git commit -m 'Initial commit'"
    )

    # 1. Initial prompt to Claude
    prompt = f"Can you clone the repository at {test_repo} to {clone_path}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "clone_repository"
    assert tool_use.input["url"] == str(test_repo)
    assert tool_use.input["path"] == str(clone_path)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    assert (clone_path / ".git").exists()
    assert (clone_path / "test.txt").exists()
    response = client.send_message(
        tool_response=f"Repository cloned successfully from {test_repo} to {clone_path}",
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

    # Create a test repo with an initial commit
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")
    os.system(
        f"cd {test_repo} && git init && git add . && git commit -m 'Initial commit'"
    )

    # 1. Initial prompt to Claude
    prompt = f"What's the current branch in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "get_current_branch"
    assert tool_use.input["repo_path"] == str(test_repo)

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

    # Create a test repo with an initial commit
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")
    os.system(
        f"""
        cd {test_repo} &&
        git init &&
        git add . &&
        git commit -m 'Initial commit' &&
        git branch feature &&
        git branch -v &&  # Debug: list branches with commit info
        git status &&  # Debug: show current status
        git branch  # Debug: list branches
    """
    )

    # 1. Initial prompt to Claude
    prompt = f"Can you create a new branch called 'feature' in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "create_branch"
    assert tool_use.input["repo_path"] == str(test_repo)
    assert tool_use.input["branch_name"] == "feature"

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    # Verify branch exists by listing branches
    branches = os.popen(f"cd {test_repo} && git branch").read()
    assert "feature" in branches
    response = client.send_message(
        tool_response=f"Created new branch 'feature' in repository at {test_repo}",
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

    # Create a test repo with an initial commit and a feature branch
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")

    # Initialize repo and create feature branch
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create and checkout feature branch
    feature_branch = repo.create_head("feature")
    feature_branch.checkout()

    # Switch back to master branch
    master = repo.heads["master"]
    master.checkout()

    # 1. Initial prompt to Claude
    prompt = f"Can you switch to the 'feature' branch in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "checkout_branch"
    assert tool_use.input["repo_path"] == str(test_repo)
    assert tool_use.input["branch_name"] == "feature"

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    if not result["success"]:
        print(
            f"Checkout failed: {result.get('error', 'No error message')}"
        )  # Debug output
        print("Current branches:")
        for head in repo.heads:
            print(f"- {head.name}")
    assert result["success"]

    # Verify current branch is feature
    assert repo.active_branch.name == "feature"

    response = client.send_message(
        tool_response=f"Switched to branch 'feature' in repository at {test_repo}",
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

    # Create a test repo with an initial commit and a new file to commit
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")
    os.system(
        f"cd {test_repo} && git init && git add . && git commit -m 'Initial commit'"
    )

    # Create a new file to commit
    new_file = test_repo / "new_file.txt"
    new_file.write_text("New content")

    # 1. Initial prompt to Claude
    prompt = f"Can you commit the new file in the repository at {test_repo} with the message 'Add new file'?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "make_commit"
    assert tool_use.input["repo_path"] == str(test_repo)
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

    # Create a test repo with multiple branches
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")

    # Initialize repo and create branches
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create feature and develop branches
    repo.create_head("feature")
    repo.create_head("develop")

    # 1. Initial prompt to Claude
    prompt = f"Can you list all branches in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "list_branches"
    assert tool_use.input["repo_path"] == str(test_repo)

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

    # Create a test repo and a remote repo
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")
    os.system(
        f"cd {test_repo} && git init && git add . && git commit -m 'Initial commit'"
    )

    remote_path = test_repo / "remote_repo"
    os.system(f"git init {remote_path}")

    # 1. Initial prompt to Claude
    prompt = f"Can you add a remote called 'upstream' pointing to {remote_path} in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "add_remote"
    assert tool_use.input["repo_path"] == str(test_repo)
    assert tool_use.input["name"] == "upstream"
    assert tool_use.input["url"] == str(remote_path)

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    # Verify remote was added
    remotes = os.popen(f"cd {test_repo} && git remote -v").read()
    assert "upstream" in remotes
    assert str(remote_path) in remotes


def test_fetch_remote(setup_environment, test_repo):
    """Test fetching from a remote with proper conversation cycle."""
    client = setup_environment

    # Create a test repo with a remote
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")

    # Initialize repo and configure user
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Add the remote
    repo.create_remote("origin", "https://github.com/octocat/Hello-World.git")

    # 1. Initial prompt to Claude
    prompt = f"Can you fetch from the 'origin' remote in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "fetch_remote"
    assert tool_use.input["repo_path"] == str(test_repo)
    # remote_name is optional since it has a default value of "origin"
    if "remote_name" in tool_use.input:
        assert tool_use.input["remote_name"] == "origin"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    # Note: We can't verify the fetch result since we're using a public repo URL
    # and the fetch might fail due to network issues


def test_pull_remote(setup_environment, test_repo):
    """Test pulling from a remote with proper conversation cycle."""
    client = setup_environment

    # Create a test repo with a remote
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")

    # Initialize repo and configure user
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()
    repo.config_writer().set_value("pull", "rebase", "false").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Add the remote and fetch
    repo.create_remote("origin", "https://github.com/octocat/Hello-World.git")
    repo.remotes.origin.fetch()

    # 1. Initial prompt to Claude
    prompt = f"Can you pull from the 'origin' remote's master branch in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "pull_remote"
    assert tool_use.input["repo_path"] == str(test_repo)
    # remote_name and branch are optional since they have default values
    if "remote_name" in tool_use.input:
        assert tool_use.input["remote_name"] == "origin"
    if "branch" in tool_use.input:
        assert tool_use.input["branch"] == "master"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    # Note: We can't verify the pull result since we're using a public repo URL
    # and the pull might fail due to network issues


def test_push_remote(setup_environment, test_repo):
    """Test pushing to a remote with proper conversation cycle."""
    client = setup_environment

    # Create a test repo with a remote
    test_file = test_repo / "test.txt"
    test_file.write_text("Hello, world!")

    # Initialize repo and configure user
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    initial_commit = repo.index.commit("Initial commit")

    # Create a bare repository to serve as remote
    remote_path = test_repo / "remote_repo.git"
    remote_repo = Repo.init(remote_path, bare=True)

    # Add the remote
    repo.create_remote("origin", str(remote_path))

    # 1. Initial prompt to Claude
    prompt = f"Can you push to the 'origin' remote in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "push_remote"
    assert tool_use.input["repo_path"] == str(test_repo)
    # remote_name is optional since it has a default value of "origin"
    if "remote_name" in tool_use.input:
        assert tool_use.input["remote_name"] == "origin"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]

    # Verify the push by checking the remote refs
    remote_refs = remote_repo.git.show_ref().split("\n")
    assert any(initial_commit.hexsha in ref for ref in remote_refs)


def test_check_for_conflicts(setup_environment, test_repo):
    """Test checking for conflicts with proper conversation cycle."""
    client = setup_environment

    # Create a test repo with conflicting changes
    test_file = test_repo / "test.txt"
    test_file.write_text("Line 1\nOriginal content\nLine 3")

    # Initialize repo and configure user
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create and checkout feature branch
    feature_branch = repo.create_head("feature")
    feature_branch.checkout()

    # Make changes in feature branch
    test_file.write_text("Line 1\nFeature branch content\nLine 3")
    repo.index.add([str(test_file)])
    repo.index.commit("Feature branch commit")

    # Switch back to master and make conflicting changes
    repo.heads.master.checkout()
    test_file.write_text("Line 1\nMaster branch content\nLine 3")
    repo.index.add([str(test_file)])
    repo.index.commit("Master branch commit")

    # Try to merge feature branch to create conflict
    try:
        repo.git.merge("feature")
    except GitCommandError:
        pass  # Merge conflict is expected

    # 1. Initial prompt to Claude
    prompt = f"Can you check if there are any merge conflicts in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "check_for_conflicts"
    assert tool_use.input["repo_path"] == str(test_repo)

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    assert result["has_conflicts"]
    assert "test.txt" in result["conflicting_files"]


def test_get_conflict_info(setup_environment, test_repo):
    """Test getting conflict info with proper conversation cycle."""
    client = setup_environment

    # Create a test repo with conflicting changes
    test_file = test_repo / "test.txt"
    test_file.write_text("Line 1\nOriginal content\nLine 3")

    # Initialize repo and configure user
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create and checkout feature branch
    feature_branch = repo.create_head("feature")
    feature_branch.checkout()

    # Make changes in feature branch
    test_file.write_text("Line 1\nFeature branch content\nLine 3")
    repo.index.add([str(test_file)])
    repo.index.commit("Feature branch commit")

    # Switch back to master and make conflicting changes
    repo.heads.master.checkout()
    test_file.write_text("Line 1\nMaster branch content\nLine 3")
    repo.index.add([str(test_file)])
    repo.index.commit("Master branch commit")

    # Try to merge feature branch to create conflict
    try:
        repo.git.merge("feature")
    except GitCommandError:
        # Verify that the conflict was created
        assert repo.index.unmerged_blobs()
        assert "test.txt" in repo.index.unmerged_blobs()

    # 1. Initial prompt to Claude
    prompt = f"Can you get information about the merge conflicts in the repository at {test_repo}?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "get_conflict_info"
    assert tool_use.input["repo_path"] == str(test_repo)

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    assert "test.txt" in result["conflicts"]
    assert "content" in result["conflicts"]["test.txt"]
    assert "ours" in result["conflicts"]["test.txt"]["content"]
    assert "theirs" in result["conflicts"]["test.txt"]["content"]


def test_resolve_conflict(setup_environment, test_repo):
    """Test resolving a conflict with proper conversation cycle."""
    client = setup_environment

    # Create a test repo with conflicting changes
    test_file = test_repo / "test.txt"
    test_file.write_text("Line 1\nOriginal content\nLine 3")

    # Initialize repo and configure user
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create and checkout feature branch
    feature_branch = repo.create_head("feature")
    feature_branch.checkout()

    # Make changes in feature branch
    test_file.write_text("Line 1\nFeature branch content\nLine 3")
    repo.index.add([str(test_file)])
    repo.index.commit("Feature branch commit")

    # Switch back to master and make conflicting changes
    repo.heads.master.checkout()
    test_file.write_text("Line 1\nMaster branch content\nLine 3")
    repo.index.add([str(test_file)])
    repo.index.commit("Master branch commit")

    # Try to merge feature branch to create conflict
    try:
        repo.git.merge("feature")
    except GitCommandError:
        pass  # Merge conflict is expected

    # 1. Initial prompt to Claude
    prompt = (
        f"Can you resolve the conflict in test.txt with the content 'Resolved content' "
        f"in the repository at {test_repo}?"
    )
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "resolve_conflict"
    assert tool_use.input["repo_path"] == str(test_repo)
    assert tool_use.input["file_path"] == "test.txt"
    assert tool_use.input["resolution"] == "Resolved content"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    # Verify file was resolved
    assert test_file.read_text() == "Resolved content"
    # Verify file is staged
    status = repo.git.status(porcelain=True)
    assert "M  test.txt" in status  # M with two spaces means staged modification


def test_create_merge_commit(setup_environment, test_repo):
    """Test creating a merge commit with proper conversation cycle."""
    client = setup_environment

    # Create a test repo with resolved conflicts
    test_file = test_repo / "test.txt"
    test_file.write_text("Line 1\nOriginal content\nLine 3")

    # Initialize repo and configure user
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create and checkout feature branch
    feature_branch = repo.create_head("feature")
    feature_branch.checkout()

    # Make changes in feature branch
    test_file.write_text("Line 1\nFeature branch content\nLine 3")
    repo.index.add([str(test_file)])
    repo.index.commit("Feature branch commit")

    # Switch back to master and make conflicting changes
    repo.heads.master.checkout()
    test_file.write_text("Line 1\nMaster branch content\nLine 3")
    repo.index.add([str(test_file)])
    repo.index.commit("Master branch commit")

    # Try to merge feature branch to create conflict
    try:
        repo.git.merge("feature")
    except GitCommandError:
        pass  # Merge conflict is expected

    # Resolve the conflict
    test_file.write_text("Line 1\nResolved content\nLine 3")
    repo.git.add("test.txt")

    # 1. Initial prompt to Claude
    prompt = f"Can you create a merge commit in the repository at {test_repo} with the message 'Merge feature branch'?"
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "create_merge_commit"
    assert tool_use.input["repo_path"] == str(test_repo)
    assert tool_use.input["message"] == "Merge feature branch"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]
    # Verify merge commit was created
    log = repo.git.log("--oneline")
    assert "Merge feature branch" in log


def test_commit_and_push(setup_environment, test_repo):
    """Test committing and pushing changes with proper conversation cycle."""
    client = setup_environment

    # Create a test repo with a remote
    test_file = test_repo / "test.txt"
    test_file.write_text("Line 1\nOriginal content\nLine 3")

    # Initialize repo and configure user
    repo = Repo.init(test_repo)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Add and commit the test file
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create a bare repository to serve as remote
    remote_path = test_repo / "remote_repo.git"
    remote_repo = Repo.init(remote_path, bare=True)

    # Add the remote and push initial commit
    repo.create_remote("origin", str(remote_path))
    repo.remotes.origin.push(repo.heads.master)

    # Make changes to test file
    test_file.write_text("Line 1\nModified content\nLine 3")

    # 1. Initial prompt to Claude
    prompt = (
        f"Can you commit the file 'test.txt' with message 'Update test.txt' and push to origin "
        f"in the repository at {test_repo}?"
    )
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "commit_and_push"
    assert tool_use.input["repo_path"] == str(test_repo)
    assert tool_use.input["message"] == "Update test.txt"
    assert tool_use.input["file_path"] == "test.txt"
    # remote_name is optional since it has a default value of "origin"
    if "remote_name" in tool_use.input:
        assert tool_use.input["remote_name"] == "origin"

    # 3. Execute tool and verify result
    result = client.execute_tool(tool_use)
    assert result["success"]

    # Verify the commit and push
    assert "Modified content" in test_file.read_text()
    remote_refs = remote_repo.git.show_ref().split("\n")
    latest_commit = repo.head.commit.hexsha
    assert any(latest_commit in ref for ref in remote_refs)


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
