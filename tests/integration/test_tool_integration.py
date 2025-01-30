"""Integration tests for tool usage with Claude."""

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
