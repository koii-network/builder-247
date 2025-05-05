import pytest
import requests
from unittest.mock import patch
from prometheus_swarm.tools.dad_joke_command import get_dad_joke, dad_joke_command_handler

def test_get_dad_joke_success():
    """Test successful dad joke retrieval."""
    with patch('requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.text = "Why don't scientists trust atoms? Because they make up everything!"
        mock_response.raise_for_status = lambda: None
        
        joke = get_dad_joke()
        assert joke == "Why don't scientists trust atoms? Because they make up everything!"
        mock_get.assert_called_once_with(
            'https://icanhazdadjoke.com/', 
            headers={
                'Accept': 'text/plain',
                'User-Agent': 'Prometheus Swarm Dad Joke Command'
            }
        )

def test_get_dad_joke_network_error():
    """Test error handling when network request fails."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(RuntimeError, match="Failed to fetch dad joke: Network error"):
            get_dad_joke()

def test_dad_joke_command_handler_success():
    """Test dad joke command handler with successful joke retrieval."""
    with patch('prometheus_swarm.tools.dad_joke_command.get_dad_joke') as mock_get_joke:
        mock_get_joke.return_value = "I told my wife she was drawing her eyebrows too high. She looked surprised."
        
        result = dad_joke_command_handler({})
        assert result['success'] is True
        assert result['message'] == "I told my wife she was drawing her eyebrows too high. She looked surprised."

def test_dad_joke_command_handler_error():
    """Test dad joke command handler when joke retrieval fails."""
    with patch('prometheus_swarm.tools.dad_joke_command.get_dad_joke') as mock_get_joke:
        mock_get_joke.side_effect = RuntimeError("Joke retrieval failed")
        
        result = dad_joke_command_handler({})
        assert result['success'] is False
        assert result['message'] == "Joke retrieval failed"