import pytest
import requests
from unittest.mock import patch
from prometheus_swarm.tools.execute_command.dad_joke_command import get_dad_joke, dad_joke_command_handler

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(f"HTTP Error {self.status_code}")

def test_get_dad_joke_success():
    """Test successful dad joke retrieval"""
    mock_joke = {
        'id': '123',
        'joke': 'Why do programmers prefer dark mode? Light attracts bugs!'
    }
    
    with patch('requests.get') as mock_get:
        mock_get.return_value = MockResponse(mock_joke)
        
        result = get_dad_joke()
        
        assert result['status'] == 'success'
        assert result['joke'] == mock_joke['joke']
        assert result['id'] == mock_joke['id']

def test_get_dad_joke_network_error():
    """Test handling of network errors"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network Error")
        
        result = get_dad_joke()
        
        assert result['status'] == 'error'
        assert 'Failed to fetch dad joke' in result['message']

def test_dad_joke_command_handler():
    """Test dad joke command handler"""
    with patch('prometheus_swarm.tools.execute_command.dad_joke_command.get_dad_joke') as mock_get_joke:
        mock_get_joke.return_value = {
            'status': 'success',
            'joke': 'Test dad joke',
            'id': '456'
        }
        
        result = dad_joke_command_handler()
        
        assert result['status'] == 'success'
        assert result['joke'] == 'Test dad joke'
        assert result['id'] == '456'

def test_dad_joke_command_handler_with_args():
    """Test dad joke command handler with optional arguments"""
    with patch('prometheus_swarm.tools.execute_command.dad_joke_command.get_dad_joke') as mock_get_joke:
        mock_get_joke.return_value = {
            'status': 'success',
            'joke': 'Test dad joke',
            'id': '456'
        }
        
        result = dad_joke_command_handler(args={'optional': 'parameter'})
        
        assert result['status'] == 'success'
        assert result['joke'] == 'Test dad joke'
        assert result['id'] == '456'