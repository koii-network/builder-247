"""Integration tests for tool usage with Claude."""

import os
import pytest
from dotenv import load_dotenv
from src.anthropic_client import AnthropicClient
from anthropic.types import Message
import time

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


def test_file_operations(setup_environment, tmp_path):
    """Test file operations tools."""
    client = setup_environment
    client.register_tools_from_directory("src/tools/definitions/file_operations")

    # Create test files
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello\nWorld\nTest")

    # Test read_file
    message = client.send_message(
        f"Can you read the contents of {test_file}?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "read_file"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["content"] if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Test write_file
    output_file = tmp_path / "output.txt"
    message = client.send_message(
        f"Can you create a new file at {output_file} with the content 'Test content'?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "write_file"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert output_file.exists()

    # Test copy_file
    copy_dest = tmp_path / "copy.txt"
    message = client.send_message(
        f"Can you copy the file from {output_file} to {copy_dest}?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "copy_file"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert copy_dest.exists()

    # Test move_file
    move_dest = tmp_path / "moved.txt"
    message = client.send_message(
        f"Can you move the file from {copy_dest} to {move_dest}?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "move_file"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert move_dest.exists()
    assert not copy_dest.exists()

    # Test rename_file
    renamed_file = tmp_path / "renamed.txt"
    message = client.send_message(
        f"Can you rename the file {move_dest} to {renamed_file}?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "rename_file"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert renamed_file.exists()
    assert not move_dest.exists()

    # Test delete_file
    message = client.send_message(
        f"Can you delete the file at {renamed_file}?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "delete_file"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert not renamed_file.exists()


def test_command_execution(setup_environment):
    """Test command execution tools."""
    client = setup_environment
    client.register_tools_from_directory("src/tools/definitions/command_execution")

    # Test basic command
    message = client.send_message(
        "Can you show me the first few lines of a Python file in this project?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "run_terminal_cmd"
    assert "head" in tool_use.input["command"] or "find" in tool_use.input["command"]

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["output"] if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Test command with pipes
    message = client.send_message(
        "Can you count how many Python files are in the current directory and its subdirectories?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "run_terminal_cmd"
    assert ".py" in tool_use.input["command"]

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["output"] if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)


def test_git_operations(setup_environment, test_repo):
    """Test Git operations tools."""
    client = setup_environment
    client.register_tools_from_directory("src/tools/definitions/git_operations")

    # Test init_repository
    message = client.send_message(
        f"Can you initialize a new Git repository at {test_repo}?",
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

    # Test clone_repository
    clone_path = test_repo.parent / "cloned_repo"
    message = client.send_message(
        f"Can you clone the repository at {test_repo} to {clone_path}?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "clone_repository"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Test get_current_branch
    message = client.send_message(
        f"What's the current branch in the repository at {test_repo}?",
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

    # Test create_branch
    message = client.send_message(
        f"Can you create a new branch called 'feature' in the repository at {test_repo}?",
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

    # Test checkout_branch
    message = client.send_message(
        f"Can you switch to the 'feature' branch in the repository at {test_repo}?",
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

    # Test make_commit
    test_file = test_repo / "new_file.txt"
    test_file.write_text("New content")
    message = client.send_message(
        f"Can you commit the new file in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "make_commit"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Test list_branches
    message = client.send_message(
        f"Can you list all branches in the repository at {test_repo}?",
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

    # Test add_remote
    message = client.send_message(
        f"Can you add a remote called 'upstream' pointing to {clone_path} in the repository at {test_repo}?",
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

    # Test fetch_remote
    message = client.send_message(
        f"Can you fetch from the 'upstream' remote in the repository at {test_repo}?",
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

    # Test push_remote
    message = client.send_message(
        f"Can you push to the 'upstream' remote in the repository at {test_repo}?",
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


@pytest.mark.skipif(not os.environ.get("GITHUB_TOKEN"), reason="GITHUB_TOKEN not set")
def test_github_operations(setup_environment):
    """Test GitHub operations tools."""
    client = setup_environment
    client.register_tools_from_directory("src/tools/definitions/github_operations")

    # Test check_fork_exists
    message = client.send_message(
        "Can you check if the repository torvalds/linux exists on GitHub?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "check_fork_exists"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="exists" if result["exists"] else "does not exist",
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    time.sleep(2)  # Rate limiting

    # Test fork_repository
    message = client.send_message(
        "Can you fork the hello-world repository from octocat?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "fork_repository"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    time.sleep(2)  # Rate limiting

    # Test create_pull_request
    message = client.send_message(
        "Can you create a pull request in the octocat/hello-world repository "
        "with the title 'Test PR' and description 'This is a test PR'?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "create_pull_request"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["pr_url"] if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    time.sleep(2)  # Rate limiting

    # Test get_pr_template
    message = client.send_message(
        "Can you get the PR template for this repository?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "get_pr_template"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["template"] if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    time.sleep(2)  # Rate limiting

    # Test sync_fork
    message = client.send_message(
        "Can you sync my fork of the hello-world repository with the upstream repository?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "sync_fork"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)


def test_multi_category_tool_selection(setup_environment, test_repo, tmp_path):
    """Test that Claude selects the appropriate tool across categories."""
    client = setup_environment

    # Register tools from all categories
    client.register_tools_from_directory("src/tools/definitions/file_operations")
    client.register_tools_from_directory("src/tools/definitions/execute_command")
    client.register_tools_from_directory("src/tools/definitions/git_operations")

    # Test file operations - should use read_file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    message1 = client.send_message(
        f"What's in the file at {test_file}?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message1, Message)
    assert message1.stop_reason == "tool_use"
    tool_use = next(block for block in message1.content if block.type == "tool_use")
    assert tool_use.name == "read_file"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["content"] if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message1.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Test command execution - should use run_terminal_cmd
    message2 = client.send_message(
        "What's the current working directory?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message2, Message)
    assert message2.stop_reason == "tool_use"
    tool_use = next(block for block in message2.content if block.type == "tool_use")
    assert tool_use.name == "run_terminal_cmd"
    assert "pwd" in tool_use.input["command"]

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["output"] if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message2.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)

    # Test git operations - should use get_current_branch
    message3 = client.send_message(
        f"Which branch am I on in the repository at {test_repo}?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message3, Message)
    assert message3.stop_reason == "tool_use"
    tool_use = next(block for block in message3.content if block.type == "tool_use")
    assert tool_use.name == "get_current_branch"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["branch"],
        tool_use_id=tool_use.id,
        conversation_id=message3.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)


def test_multi_step_workflow(setup_environment, tmp_path):
    """Test a workflow that requires multiple tools in sequence."""
    client = setup_environment

    # Register tools from all categories
    client.register_tools_from_directory("src/tools/definitions/file_operations")
    client.register_tools_from_directory("src/tools/definitions/execute_command")
    client.register_tools_from_directory("src/tools/definitions/git_operations")

    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")

    # Complex workflow: Read a file, modify its content, write it back, and commit it
    message = client.send_message(
        f"Can you read the file at {test_file}, add a new line saying 'New line', "
        f"write it back to the file, and commit it to a new git repository?",
        tool_choice={"type": "any"},
    )

    # Should use read_file first
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "read_file"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["content"] if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # Should use write_file next
    assert isinstance(response, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in response.content if block.type == "tool_use")
    assert tool_use.name == "write_file"
    assert "New line" in tool_use.input["content"]

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # Should use init_repository next
    assert isinstance(response, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in response.content if block.type == "tool_use")
    assert tool_use.name == "init_repository"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # Should use make_commit last
    assert isinstance(response, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in response.content if block.type == "tool_use")
    assert tool_use.name == "make_commit"

    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
