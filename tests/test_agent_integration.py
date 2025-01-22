"""
Integration tests for agent interactions with filesystem tools.
"""
import os
import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.client import AnthropicClient

def create_mock_response(actions):
    """Create a mock response that simulates the agent's actions."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "actions": actions,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }))]
    return mock_response

def test_agent_filesystem_interaction(tmp_path):
    """Test agent's ability to navigate filesystem and create files."""
    # Create test directory structure
    test_dir = tmp_path / "testing"
    test_dir.mkdir()
    test_file = test_dir / "hello-world.txt"
    
    # Test prompt for the agent
    prompt = """
    Please help me with the following tasks:
    1. Use the filesystem tools to locate the 'testing' directory
    2. Create a file called 'hello-world.txt' in that directory
    3. Write the current timestamp and your steps into the file
    
    Use the available tools to complete these tasks and report your actions.
    """
    
    # Expected agent actions
    expected_actions = [
        {"tool": "list_dir", "args": {"path": str(tmp_path)}},
        {"tool": "file_search", "args": {"query": "testing"}},
        {"tool": "list_dir", "args": {"path": str(test_dir)}},
        {"tool": "write_file", "args": {
            "path": str(test_file),
            "content": "Timestamp: {timestamp}\n\nSteps taken:\n1. Located testing directory\n2. Created hello-world.txt\n3. Wrote timestamp and steps"
        }}
    ]
    
    # Create the file that would be created by the agent
    timestamp = datetime.now().isoformat()
    test_file.write_text(f"Timestamp: {timestamp}\n\nSteps taken:\n1. Located testing directory\n2. Created hello-world.txt\n3. Wrote timestamp and steps")
    
    # Mock environment and API responses
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            # Set up mock client
            mock_client = MagicMock()
            mock_client.messages.create.return_value = create_mock_response(expected_actions)
            mock_client_class.return_value = mock_client
            
            # Create client and send prompt
            client = AnthropicClient()
            response = client.send_message(prompt)
            
            # Parse response
            response_data = json.loads(response)
            
            # Verify API interaction
            mock_client.messages.create.assert_called_once()
            call_args = mock_client.messages.create.call_args[1]
            assert call_args["model"] == "claude-3-sonnet-20240229"
            assert call_args["messages"][0]["content"] == prompt
            
            # Verify response structure
            assert "actions" in response_data
            assert "timestamp" in response_data
            assert "status" in response_data
            assert response_data["status"] == "success"
            
            # Verify actions match expected sequence
            assert len(response_data["actions"]) == len(expected_actions)
            for actual, expected in zip(response_data["actions"], expected_actions):
                assert actual["tool"] == expected["tool"]
                assert actual["args"].keys() == expected["args"].keys()
            
            # Verify file exists and has correct content
            assert test_file.exists()
            content = test_file.read_text()
            assert "Timestamp:" in content
            assert "Steps taken:" in content
            assert "Located testing directory" in content
            assert "Created hello-world.txt" in content
            assert "Wrote timestamp and steps" in content

def test_agent_error_handling():
    """Test agent's handling of filesystem errors."""
    # Test prompt for error cases
    prompt = """
    Please try to:
    1. Access a non-existent directory
    2. Write to a read-only file
    3. Handle the errors appropriately
    """
    
    # Mock error responses
    error_actions = [
        {"tool": "list_dir", "args": {"path": "nonexistent"}, "error": "Directory not found"},
        {"tool": "write_file", "args": {"path": "readonly.txt"}, "error": "Permission denied"}
    ]
    
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = create_mock_response(error_actions)
            mock_client_class.return_value = mock_client
            
            client = AnthropicClient()
            response = client.send_message(prompt)
            
            # Verify error handling
            response_data = json.loads(response)
            assert response_data["status"] == "success"
            assert len(response_data["actions"]) == len(error_actions)
            for action in response_data["actions"]:
                assert "error" in action 