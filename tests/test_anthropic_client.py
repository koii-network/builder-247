"""Tests for the client module."""

import os
import pytest
from dotenv import load_dotenv
from src.anthropic_client import AnthropicClient
from anthropic.types import ToolUseBlock, Message, ToolParam, TextBlock
import json
from pathlib import Path


@pytest.fixture(autouse=True)
def setup_environment(tmp_path):
    """Set up environment variables before each test."""
    load_dotenv()
    if not os.environ.get("CLAUDE_API_KEY"):
        pytest.skip("CLAUDE_API_KEY environment variable not set")
    api_key = os.environ.get("CLAUDE_API_KEY")
    temp_db = tmp_path / "test.db"
    yield AnthropicClient(api_key=api_key, db_path=temp_db)


@pytest.fixture
def temp_tools_dir(tmp_path):
    """Create a temporary directory with mock tool definitions and implementations."""

    # Create mock tool definition
    tool_def = {
        "name": "mock_tool",
        "description": "A mock tool for testing",
        "parameters": {
            "type": "object",
            "properties": {"input": {"type": "string", "description": "Test input"}},
            "required": ["input"],
        },
    }

    # Write tool definition
    tool_dir = Path(tmp_path)
    with open(tool_dir / "mock_tool.json", "w") as f:
        json.dump(tool_def, f)

        # Create mock implementation
        with open(tool_dir / "implementations.py", "w") as f:
            f.write(
                """
def mock_tool(input: str) -> str:
    return f"Processed: {input}"

TOOL_IMPLEMENTATIONS = {
    "mock_tool": mock_tool
}
"""
            )

    yield tool_dir


def calculator_tool():
    """Return a simple calculator tool definition."""
    return ToolParam(
        name="calculator",
        description="A simple calculator that can add two numbers",
        input_schema={
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "First number to add"},
                "y": {"type": "number", "description": "Second number to add"},
            },
            "required": ["x", "y"],
        },
    )


def calculator(x: int, y: int) -> int:
    """Return the sum of two numbers."""
    return x + y


def string_tool():
    """Return a string manipulation tool definition."""
    return ToolParam(
        name="string_reverser",
        description="A tool that reverses a string",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to reverse"},
            },
            "required": ["text"],
        },
    )


def string_reverser(text: str) -> str:
    """Return the reverse of a string."""
    return text[::-1]


@pytest.fixture
def calculator_tool_choice():
    return {"type": "tool", "name": "calculator"}


@pytest.fixture
def string_tool_choice():
    return {"type": "tool", "name": "string_reverser"}


@pytest.fixture
def multiple_tool_choice():
    return {"type": "any"}


def test_send_message(setup_environment):
    """Test that we can send a message to Claude and get a response."""
    client = setup_environment
    response = client.send_message("What is 2+2?")
    assert isinstance(response, Message)
    assert isinstance(response.content[0], TextBlock)
    assert "4" in response.content[0].text


def test_send_test_message_no_api_key(monkeypatch):
    """Test that appropriate error is raised when API key is missing."""
    # Remove the CLAUDE_API_KEY for this test
    monkeypatch.delenv("CLAUDE_API_KEY", raising=False)

    with pytest.raises(ValueError, match="Missing CLAUDE_API_KEY"):
        AnthropicClient()


def test_send_message_with_tool(setup_environment, calculator_tool_choice):
    """Test that Claude can understand and use a tool definition."""
    client = setup_environment
    client.register_tool(calculator_tool(), calculator)
    response = client.send_message(
        "I need to add 5 and 3. Can you help me with that?",
        tool_choice=calculator_tool_choice,
    )

    assert isinstance(response, Message)
    assert response.stop_reason == "tool_use"
    tool_use = [block for block in response.content if block.type == "tool_use"][0]
    assert isinstance(tool_use, ToolUseBlock)
    assert tool_use.type == "tool_use"
    assert tool_use.name == "calculator"
    assert tool_use.input == {"x": 5, "y": 3}


def test_send_message_with_tool_no_tool_needed(setup_environment):
    """Test that Claude can respond without using the tool when not needed."""
    client = setup_environment
    client.register_tool(calculator_tool(), calculator)
    response = client.send_message(
        "What is your name?",
    )
    print(response)

    assert isinstance(response, Message)
    assert isinstance(response.content[0], TextBlock)


def test_send_message_with_multiple_tools(
    setup_environment,
    multiple_tool_choice,
):
    """Test that Claude can understand and use multiple tools."""
    client = setup_environment
    client.register_tool(calculator_tool(), calculator)
    client.register_tool(string_tool(), string_reverser)
    message1 = client.send_message(
        "I need to add 5 and 3. Can you help me with that?",
        tool_choice=multiple_tool_choice,
    )

    assert isinstance(message1, Message)
    assert message1.stop_reason == "tool_use"
    tool_use = [block for block in message1.content if block.type == "tool_use"][0]
    assert isinstance(tool_use, ToolUseBlock)
    assert tool_use.type == "tool_use"
    assert tool_use.name == "calculator"
    assert tool_use.input == {"x": 5, "y": 3}

    message2 = client.send_message(
        "What is the reverse of 'hello'?",
        tool_choice=multiple_tool_choice,
    )

    assert isinstance(message2, Message)
    assert message2.stop_reason == "tool_use"
    tool_use = [block for block in message2.content if block.type == "tool_use"][0]
    assert isinstance(tool_use, ToolUseBlock)
    assert tool_use.type == "tool_use"
    assert tool_use.name == "string_reverser"
    assert tool_use.input == {"text": "hello"}


def test_send_message_with_tool_response(setup_environment, string_tool_choice):
    """Test that Claude can respond to a tool call."""
    client = setup_environment
    client.register_tool(string_tool(), string_reverser)
    message1 = client.send_message(
        "What is the reverse of 'hello'?",
        tool_choice=string_tool_choice,
    )
    print("Message 1:", message1)

    assert isinstance(message1, Message)
    assert message1.stop_reason == "tool_use"
    tool_use = [block for block in message1.content if block.type == "tool_use"][0]
    assert isinstance(tool_use, ToolUseBlock)
    assert tool_use.type == "tool_use"
    assert tool_use.name == "string_reverser"
    assert tool_use.input == {"text": "hello"}

    message2 = client.send_message(
        previous_messages=[
            {"role": "user", "content": "What is the reverse of 'hello'?"},
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": tool_use.id,
                        "name": tool_use.name,
                        "input": tool_use.input,
                    }
                ],
            },
        ],
        tool_response="olleh",
        tool_use_id=tool_use.id,
    )
    print("Message 2:", message2)
    assert isinstance(message2, Message)
    assert isinstance(message2.content[0], TextBlock)
    assert "olleh" in message2.content[0].text


def test_conversation_creation(setup_environment):
    """Test creating a new conversation."""
    client = setup_environment

    # Send initial message
    response = client.send_message("Hello!")

    assert isinstance(response, Message)
    assert isinstance(response.content[0], TextBlock)


def test_conversation_persistence(setup_environment):
    """Test that conversations persist between client instances."""
    # First client instance
    client1 = setup_environment
    response1 = client1.send_message("Remember this: BLUE")

    # Second client instance
    client2 = setup_environment
    response2 = client2.send_message("What did I ask you to remember?")

    assert isinstance(response1, Message)
    assert isinstance(response2, Message)
    assert isinstance(response1.content[0], TextBlock)
    assert isinstance(response2.content[0], TextBlock)


def test_bulk_tool_registration(temp_tools_dir, setup_environment):
    """Test registering tools from a directory."""
    client = setup_environment
    registered_tools = client.register_tools_from_directory(temp_tools_dir)

    assert len(registered_tools) == 1
    assert registered_tools[0] == "mock_tool"
    assert len(client.tools) == 1
    assert "mock_tool" in client.tool_functions

    # Test using the registered tool
    response = client.send_message(
        "Process this text: test", tool_choice={"type": "tool", "name": "mock_tool"}
    )

    assert isinstance(response, Message)
    assert isinstance(response.content[0], TextBlock)


def test_bulk_registration_errors(tmp_path):
    """Test error handling in bulk tool registration."""
    client = setup_environment

    # Test with non-existent directory
    with pytest.raises(ValueError, match="Directory not found"):
        client.register_tools_from_directory("/nonexistent/path")

    # Test with missing implementations.py
    with pytest.raises(ValueError, match="Missing implementations.py"):
        client.register_tools_from_directory(tmp_path)


def test_conversation_with_tools(temp_tools_dir, setup_environment):
    """Test using tools within a persistent conversation."""
    client = setup_environment
    client.register_tools_from_directory(temp_tools_dir)

    # Start conversation
    response1 = client.send_message(
        "Process this: hello", tool_choice={"type": "tool", "name": "mock_tool"}
    )

    # Continue conversation
    response2 = client.send_message(
        "Process this: world", tool_choice={"type": "tool", "name": "mock_tool"}
    )

    assert isinstance(response1, Message)
    assert isinstance(response2, Message)
    assert isinstance(response1.content[0], TextBlock)
    assert isinstance(response2.content[0], TextBlock)
