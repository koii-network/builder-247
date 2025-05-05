"""
Unit tests for Dad Joke Command Handler.
"""

import pytest
from unittest.mock import patch, Mock
from prometheus_swarm.tools.dad_joke_handler import DadJokeCommandHandler


def test_dad_joke_handler_initialization():
    """Test initializing the Dad Joke Command Handler."""
    handler = DadJokeCommandHandler()
    assert isinstance(handler, DadJokeCommandHandler)
    assert handler.joke_history == []


@patch('requests.get')
def test_get_random_joke_success(mock_get):
    """Test successfully retrieving a random dad joke."""
    mock_response = Mock()
    mock_response.text = "Why don't scientists trust atoms? Because they make up everything!"
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    handler = DadJokeCommandHandler()
    joke = handler.get_random_joke()

    assert joke == "Why don't scientists trust atoms? Because they make up everything!"
    assert handler.joke_history == [joke]


@patch('requests.get')
def test_get_random_joke_failure(mock_get):
    """Test handling failure when retrieving a dad joke."""
    mock_get.side_effect = requests.RequestException("Network error")

    handler = DadJokeCommandHandler()
    with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
        handler.get_random_joke()


def test_get_joke_history():
    """Test retrieving joke history."""
    handler = DadJokeCommandHandler()
    jokes = ["Joke 1", "Joke 2", "Joke 3"]
    handler.joke_history = jokes

    # Get full history
    assert handler.get_joke_history() == jokes

    # Get limited history
    assert handler.get_joke_history(2) == ["Joke 1", "Joke 2"]


def test_clear_joke_history():
    """Test clearing joke history."""
    handler = DadJokeCommandHandler()
    handler.joke_history = ["Joke 1", "Joke 2"]
    
    handler.clear_joke_history()
    assert handler.joke_history == []


def test_handle_command_random():
    """Test handle_command with 'random' command."""
    with patch.object(DadJokeCommandHandler, 'get_random_joke', return_value="A funny joke"):
        handler = DadJokeCommandHandler()
        result = handler.handle_command("random")
        assert result == {"joke": "A funny joke"}


def test_handle_command_history():
    """Test handle_command with 'history' command."""
    handler = DadJokeCommandHandler()
    handler.joke_history = ["Joke 1", "Joke 2", "Joke 3"]
    
    result = handler.handle_command("history")
    assert result == {"history": ["Joke 1", "Joke 2", "Joke 3"]}

    result_limited = handler.handle_command("history", limit=2)
    assert result_limited == {"history": ["Joke 1", "Joke 2"]}


def test_handle_command_clear_history():
    """Test handle_command with 'clear_history' command."""
    handler = DadJokeCommandHandler()
    handler.joke_history = ["Joke 1", "Joke 2"]
    
    result = handler.handle_command("clear_history")
    assert result == {"status": "Joke history cleared"}
    assert handler.joke_history == []


def test_handle_command_unknown():
    """Test handle_command with an unknown command."""
    handler = DadJokeCommandHandler()
    with pytest.raises(ValueError, match="Unknown command"):
        handler.handle_command("invalid_command")