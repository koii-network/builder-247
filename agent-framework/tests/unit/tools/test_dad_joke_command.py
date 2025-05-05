import pytest
import requests
from unittest.mock import patch
from prometheus_swarm.tools.dad_joke_command import get_dad_joke

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

def test_get_dad_joke_success():
    # Mock a successful API response
    mock_joke = "Why don't scientists trust atoms? Because they make up everything!"
    mock_response = MockResponse({'joke': mock_joke}, 200)

    with patch('requests.get', return_value=mock_response) as mock_get:
        result = get_dad_joke()
        
        # Verify the API was called
        mock_get.assert_called_once_with(
            'https://icanhazdadjoke.com/', 
            headers={
                'Accept': 'application/json',
                'User-Agent': 'Prometheus Swarm Dad Joke Command'
            }
        )
        
        # Check the result structure and content
        assert result['status'] == 'success'
        assert result['joke'] == mock_joke

def test_get_dad_joke_api_error():
    # Mock an API error response
    mock_response = MockResponse({}, 500)

    with patch('requests.get', return_value=mock_response):
        result = get_dad_joke()
        
        assert result['status'] == 'error'
        assert result['error_code'] == 500
        assert result['joke'] == 'Failed to fetch dad joke'

def test_get_dad_joke_network_error():
    # Mock a network error
    with patch('requests.get', side_effect=requests.RequestException('Network error')):
        result = get_dad_joke()
        
        assert result['status'] == 'error'
        assert 'Network error occurred while fetching dad joke' in result['joke']
        assert 'Network error' in result['error']