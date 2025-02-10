"""Integration tests for command execution tools."""

import os
import pytest
from src.anthropic_client import AnthropicClient
from anthropic.types import Message


@pytest.fixture(autouse=True)
def setup_environment(tmp_path):
    """Set up environment variables and client before each test."""
    api_key = os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        pytest.skip("CLAUDE_API_KEY environment variable not set")
    temp_db = tmp_path / "test.db"
    client = AnthropicClient(api_key=api_key, db_path=temp_db)
    client.register_tools_from_directory("src/tools/definitions/execute_command")
    return client


def test_command_execution(setup_environment, tmp_path):
    """Test command execution tool."""
    client = setup_environment

    # Create a test file
    with open("test.txt", "w") as f:
        f.write("test content")

    # Execute ls command
    message = client.send_message(
        "Can you list the files in the current directory?",
        tool_choice={"type": "any"},
    )

    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "execute_command"

    # Execute tool and get stdout, stderr, returncode
    stdout, stderr, returncode = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=stdout if returncode == 0 else stderr,
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert "test.txt" in stdout
    assert returncode == 0

    # Clean up
    os.remove("test.txt")
