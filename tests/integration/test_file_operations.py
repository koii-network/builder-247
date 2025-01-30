"""Integration tests for file operations tools."""

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
    client.register_tools_from_directory("src/tools/definitions/file_operations")
    return client


def test_read_file(setup_environment, tmp_path):
    """Test the read_file tool with proper conversation cycle."""
    client = setup_environment

    # Create a test file with specific content
    test_file = tmp_path / "test.txt"
    test_content = "Hello\nWorld\nTest"
    test_file.write_text(test_content)

    # 1. Initial prompt to Claude
    prompt = (
        f"I have a text file located at {test_file} that contains some text. "
        "Could you read its contents and tell me what's in it?"
    )
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "read_file"
    assert tool_use.input["file_path"] == str(test_file)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    response = client.send_message(
        tool_response=result["content"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    final_text = response.content[0].text
    assert "Hello" in final_text
    assert "World" in final_text
    assert "Test" in final_text


def test_write_file(setup_environment, tmp_path):
    """Test the write_file tool with proper conversation cycle."""
    client = setup_environment
    output_file = tmp_path / "output.txt"

    # 1. Initial prompt to Claude
    prompt = (
        f"I need you to create a new text file at {output_file} with the following content:\n"
        "Test content\n"
        "Could you help me write this file?"
    )
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "write_file"
    assert tool_use.input["file_path"] == str(output_file)
    assert tool_use.input["content"] == "Test content"

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response and file system state
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert output_file.exists()
    assert output_file.read_text() == "Test content"


def test_copy_file(setup_environment, tmp_path):
    """Test the copy_file tool with proper conversation cycle."""
    client = setup_environment

    # Create a test file with specific content
    source_file = tmp_path / "source.txt"
    source_file.write_text("Test content")
    dest_file = tmp_path / "dest.txt"

    # 1. Initial prompt to Claude
    prompt = (
        f"I have a file at {source_file} that I need to copy to {dest_file}. "
        "Could you help me copy this file?"
    )
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "copy_file"
    assert tool_use.input["source_path"] == str(source_file)
    assert tool_use.input["dest_path"] == str(dest_file)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response and file system state
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert dest_file.exists()
    assert dest_file.read_text() == "Test content"


def test_move_file(setup_environment, tmp_path):
    """Test the move_file tool with proper conversation cycle."""
    client = setup_environment

    # Create a test file with specific content
    source_file = tmp_path / "source.txt"
    source_file.write_text("Test content")
    dest_file = tmp_path / "dest.txt"

    # 1. Initial prompt to Claude
    prompt = (
        f"I have a file at {source_file} that I need to move to {dest_file}. "
        "Could you help me move this file?"
    )
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "move_file"
    assert tool_use.input["source_path"] == str(source_file)
    assert tool_use.input["dest_path"] == str(dest_file)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response and file system state
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert dest_file.exists()
    assert not source_file.exists()
    assert dest_file.read_text() == "Test content"


def test_rename_file(setup_environment, tmp_path):
    """Test the rename_file tool with proper conversation cycle."""
    client = setup_environment

    # Create a test file with specific content
    source_file = tmp_path / "old_name.txt"
    source_file.write_text("Test content")
    dest_file = tmp_path / "new_name.txt"

    # 1. Initial prompt to Claude
    prompt = (
        f"I have a file at {source_file} that I need to rename to {dest_file}. "
        "Could you help me rename this file?"
    )
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "rename_file"
    assert tool_use.input["source_path"] == str(source_file)
    assert tool_use.input["dest_path"] == str(dest_file)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response and file system state
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert dest_file.exists()
    assert not source_file.exists()
    assert dest_file.read_text() == "Test content"


def test_delete_file(setup_environment, tmp_path):
    """Test the delete_file tool with proper conversation cycle."""
    client = setup_environment

    # Create a test file to delete
    test_file = tmp_path / "to_delete.txt"
    test_file.write_text("Test content")

    # 1. Initial prompt to Claude
    prompt = (
        f"I have a file at {test_file} that I need to delete. "
        "Could you help me delete this file?"
    )
    message = client.send_message(prompt, tool_choice={"type": "any"})

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "delete_file"
    assert tool_use.input["file_path"] == str(test_file)

    # 3. Execute tool and send result back in the same conversation
    result = client.execute_tool(tool_use)
    assert result["success"]
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Verify Claude's final response and file system state
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert not test_file.exists()
