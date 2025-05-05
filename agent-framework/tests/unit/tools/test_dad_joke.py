import pytest
import requests_mock
from prometheus_swarm.tools.execute_command.implementations import get_dad_joke

def test_get_dad_joke_success():
    """Test successful dad joke retrieval."""
    with requests_mock.Mocker() as m:
        # Mock a successful API response
        mock_joke = "Why don't scientists trust atoms? Because they make up everything!"
        m.get('https://icanhazdadjoke.com/', 
              json={'joke': mock_joke}, 
              status_code=200)
        
        result = get_dad_joke()
        
        assert result['success'] is True
        assert result['message'] == mock_joke
        assert result['data']['joke'] == mock_joke

def test_get_dad_joke_api_error():
    """Test handling of API errors."""
    with requests_mock.Mocker() as m:
        # Simulate an API error
        m.get('https://icanhazdadjoke.com/', status_code=500)
        
        result = get_dad_joke()
        
        assert result['success'] is False
        assert 'Failed to fetch dad joke' in result['message']

def test_get_dad_joke_no_joke():
    """Test handling of response without a joke."""
    with requests_mock.Mocker() as m:
        # Simulate an API response without a joke
        m.get('https://icanhazdadjoke.com/', 
              json={}, 
              status_code=200)
        
        result = get_dad_joke()
        
        assert result['success'] is False
        assert 'No joke found in the response' in result['message']