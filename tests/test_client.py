"""
Tests for the Anthropic client wrapper.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from src.client import AnthropicClient

def test_client_initialization():
    """Test client initialization with API key."""
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client:
            client = AnthropicClient()
            assert client.model == "claude-3-sonnet-20240229"
            assert client.conversation_history == []

def test_send_message():
    """Test sending a message to Claude."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello, world!")]
    
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = AnthropicClient()
            response = client.send_message("Hi", system="Be helpful")
            
            assert response == "Hello, world!"
            mock_client.messages.create.assert_called_once()
            call_args = mock_client.messages.create.call_args[1]
            assert call_args["model"] == "claude-3-sonnet-20240229"
            assert call_args["messages"][0]["content"] == "Hi"
            assert call_args["system"] == "Be helpful"

def test_conversation_history():
    """Test conversation history management."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello!")]
    
    with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
        with patch("anthropic.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = AnthropicClient()
            client.send_message("Hi")
            
            assert len(client.conversation_history) == 2
            assert client.conversation_history[0]["role"] == "user"
            assert client.conversation_history[0]["content"] == "Hi"
            assert client.conversation_history[1]["role"] == "assistant"
            assert client.conversation_history[1]["content"] == "Hello!"
            
            client.clear_history()
            assert len(client.conversation_history) == 0

def test_missing_api_key():
    """Test error handling for missing API key."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("anthropic.Client") as mock_client:
            mock_client.side_effect = ValueError("API key is required")
            with pytest.raises(ValueError, match="Failed to initialize Anthropic client: API key is required"):
                AnthropicClient() 