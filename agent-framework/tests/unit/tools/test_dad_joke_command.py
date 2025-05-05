import pytest
import requests
from unittest.mock import patch
from prometheus_swarm.tools.dad_joke_command.implementations import get_dad_joke

def test_get_dad_joke_success():
    """Test successful dad joke retrieval."""
    mock_response = {
        'joke': 'Why do programmers prefer dark mode? Light attracts bugs!',
        'status_code': 200
    }
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = mock_response['status_code']
        mock_get.return_value.json.return_value = {'joke': mock_response['joke']}
        
        result = get_dad_joke()
        
        assert result['joke'] == mock_response['joke']
        assert result['status'] == mock_response['status_code']

def test_get_dad_joke_network_error():
    """Test handling of network errors."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException('Network error')
        
        result = get_dad_joke()
        
        assert 'Error fetching dad joke' in result['joke']
        assert result['status'] == 500

def test_get_dad_joke_bad_response():
    """Test handling of bad API responses."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {}
        
        result = get_dad_joke()
        
        assert result['joke'] == 'Failed to fetch dad joke'
        assert result['status'] == 404