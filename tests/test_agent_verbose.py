"""
Verbose integration tests for agent interactions with filesystem tools.
Includes detailed logging of all operations and state changes.
"""
import os
import sys
import json
import pytest
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.client import AnthropicClient

# Set up verbose logging with absolute path and immediate output
log_file = Path(__file__).parent / "verbose_agent_test.log"
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configure file handler
file_handler = logging.FileHandler(str(log_file), mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format))

# Configure console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_format))

# Configure root logger
logger = logging.getLogger('AgentVerboseTest')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.propagate = False  # Prevent duplicate logging

def create_mock_response(actions):
    """Create a mock response that simulates the agent's actions."""
    logger.info("Creating mock response with actions: %s", json.dumps(actions, indent=2))
    mock_response = MagicMock()
    response_content = {
        "actions": actions,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }
    logger.debug("Response content: %s", json.dumps(response_content, indent=2))
    mock_response.content = [MagicMock(text=json.dumps(response_content))]
    return mock_response

@pytest.fixture
def setup_test_env(tmp_path):
    """Set up test environment with detailed logging."""
    logger.info("Setting up test environment")
    logger.debug("Creating temporary directory at: %s", tmp_path)
    
    # Create test directory structure
    test_dir = tmp_path / "testing"
    test_dir.mkdir()
    logger.info("Created test directory: %s", test_dir)
    
    return test_dir

def test_agent_verbose_interaction(setup_test_env):
    """Test agent's filesystem interactions with verbose logging."""
    test_dir = setup_test_env
    test_file = test_dir / "hello-world.txt"
    logger.info("Test file path: %s", test_file)
    
    # Log test initialization
    logger.info("Starting verbose agent interaction test")
    logger.debug("Test directory: %s", test_dir)
    
    # Test prompt for the agent
    prompt = """
    Please help me with the following tasks:
    1. Use the filesystem tools to locate the 'testing' directory
    2. Create a file called 'hello-world.txt' in that directory
    3. Write the current timestamp and your steps into the file
    
    Use the available tools to complete these tasks and report your actions.
    """
    logger.info("Using test prompt: %s", prompt)
    
    # Expected agent actions
    expected_actions = [
        {"tool": "list_dir", "args": {"path": str(test_dir.parent)}},
        {"tool": "file_search", "args": {"query": "testing"}},
        {"tool": "list_dir", "args": {"path": str(test_dir)}},
        {"tool": "write_file", "args": {
            "path": str(test_file),
            "content": "Timestamp: {timestamp}\n\nSteps taken:\n1. Located testing directory\n2. Created hello-world.txt\n3. Wrote timestamp and steps"
        }}
    ]
    logger.info("Defined expected actions: %s", json.dumps(expected_actions, indent=2))
    
    # Create the file that would be created by the agent
    timestamp = datetime.now().isoformat()
    logger.debug("Using timestamp: %s", timestamp)
    content = f"Timestamp: {timestamp}\n\nSteps taken:\n1. Located testing directory\n2. Created hello-world.txt\n3. Wrote timestamp and steps"
    test_file.write_text(content)
    logger.info("Created test file with content:\n%s", content)
    
    # Mock environment and API responses
    logger.info("Setting up mock environment")
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        logger.debug("Mocked environment variables set")
        with patch("anthropic.Client") as mock_client_class:
            logger.info("Setting up mock Anthropic client")
            
            # Set up mock client
            mock_client = MagicMock()
            mock_client.messages.create.return_value = create_mock_response(expected_actions)
            mock_client_class.return_value = mock_client
            logger.debug("Mock client configured")
            
            # Create client and send prompt
            logger.info("Creating AnthropicClient instance")
            client = AnthropicClient()
            logger.info("Sending message with prompt")
            response = client.send_message(prompt)
            logger.debug("Received response: %s", response)
            
            # Parse response
            logger.info("Parsing response")
            response_data = json.loads(response)
            logger.debug("Parsed response data: %s", json.dumps(response_data, indent=2))
            
            # Verify API interaction
            logger.info("Verifying API interactions")
            mock_client.messages.create.assert_called_once()
            call_args = mock_client.messages.create.call_args[1]
            logger.debug("API call arguments: %s", json.dumps(call_args, indent=2))
            
            assert call_args["model"] == "claude-3-sonnet-20240229"
            logger.info("✓ Model verification passed")
            assert call_args["messages"][0]["content"] == prompt
            logger.info("✓ Prompt verification passed")
            
            # Verify response structure
            logger.info("Verifying response structure")
            assert "actions" in response_data
            assert "timestamp" in response_data
            assert "status" in response_data
            assert response_data["status"] == "success"
            logger.info("✓ Response structure verification passed")
            
            # Verify actions match expected sequence
            logger.info("Verifying action sequence")
            assert len(response_data["actions"]) == len(expected_actions)
            for i, (actual, expected) in enumerate(zip(response_data["actions"], expected_actions)):
                logger.debug("Checking action %d", i + 1)
                assert actual["tool"] == expected["tool"]
                assert actual["args"].keys() == expected["args"].keys()
            logger.info("✓ Action sequence verification passed")
            
            # Verify file exists and has correct content
            logger.info("Verifying file content")
            assert test_file.exists()
            content = test_file.read_text()
            logger.debug("File content:\n%s", content)
            
            assert "Timestamp:" in content
            assert "Steps taken:" in content
            assert "Located testing directory" in content
            assert "Created hello-world.txt" in content
            assert "Wrote timestamp and steps" in content
            logger.info("✓ File content verification passed")
            
    logger.info("All test verifications completed successfully")

def test_agent_verbose_error_handling(setup_test_env):
    """Test agent's error handling with verbose logging."""
    logger.info("Starting verbose error handling test")
    
    # Test prompt for error cases
    prompt = """
    Please try to:
    1. Access a non-existent directory
    2. Write to a read-only file
    3. Handle the errors appropriately
    """
    logger.info("Using error test prompt: %s", prompt)
    
    # Mock error responses
    error_actions = [
        {"tool": "list_dir", "args": {"path": "nonexistent"}, "error": "Directory not found"},
        {"tool": "write_file", "args": {"path": "readonly.txt"}, "error": "Permission denied"}
    ]
    logger.info("Defined error actions: %s", json.dumps(error_actions, indent=2))
    
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        logger.debug("Mocked environment variables set")
        with patch("anthropic.Client") as mock_client_class:
            logger.info("Setting up mock Anthropic client for error testing")
            
            mock_client = MagicMock()
            mock_client.messages.create.return_value = create_mock_response(error_actions)
            mock_client_class.return_value = mock_client
            logger.debug("Mock client configured for error testing")
            
            client = AnthropicClient()
            logger.info("Sending message with error prompt")
            response = client.send_message(prompt)
            logger.debug("Received error response: %s", response)
            
            # Verify error handling
            logger.info("Verifying error handling")
            response_data = json.loads(response)
            assert response_data["status"] == "success"
            assert len(response_data["actions"]) == len(error_actions)
            
            for i, action in enumerate(response_data["actions"]):
                logger.debug("Checking error action %d: %s", i + 1, json.dumps(action, indent=2))
                assert "error" in action
            
            logger.info("✓ Error handling verification passed")
    
    logger.info("All error handling tests completed successfully") 