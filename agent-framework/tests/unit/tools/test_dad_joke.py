import pytest
import requests
from unittest.mock import patch
from prometheus_swarm.tools.execute_command.implementations import get_dad_joke

def test_get_dad_joke_success():
    """Test successful retrieval of a random dad joke."""
    with patch('requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.json.return_value = {'joke': 'Why did the scarecrow win an award? Because he was outstanding in his field!'}
        mock_response.raise_for_status.return_value = None
        mock_response.url = 'https://icanhazdadjoke.com/'

        result = get_dad_joke()
        assert result['success'] is True
        assert 'joke' in result['data']
        assert result['data']['category'] == 'random'

def test_get_dad_joke_with_category():
    """Test dad joke retrieval with a specific category."""
    with patch('requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            'results': [{'joke': 'Why do programmers prefer dark mode? Because light attracts bugs!'}]
        }
        mock_response.raise_for_status.return_value = None
        mock_response.url = 'https://icanhazdadjoke.com/search?term=programming'

        result = get_dad_joke(category='coding')
        assert result['success'] is True
        assert 'joke' in result['data']
        assert result['data']['category'] == 'coding'

def test_get_dad_joke_invalid_category():
    """Test error handling for invalid category."""
    result = get_dad_joke(category='invalid')
    assert result['success'] is False
    assert 'Invalid category' in result['message']

def test_get_dad_joke_api_error():
    """Test error handling when joke API fails."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException('Network Error')

        result = get_dad_joke()
        assert result['success'] is False
        assert 'Failed to retrieve dad joke' in result['message']

def test_get_dad_joke_no_jokes_found():
    """Test handling of no jokes found for a specific category."""
    with patch('requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status.return_value = None
        mock_response.url = 'https://icanhazdadjoke.com/search?term=programming'

        result = get_dad_joke(category='coding')
        assert result['success'] is False
        assert 'No jokes found' in result['message']