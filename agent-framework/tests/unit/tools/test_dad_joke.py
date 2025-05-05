import pytest
import requests_mock
from prometheus_swarm.tools.execute_command.dad_joke import get_dad_joke

def test_get_dad_joke_success():
    """Test successful dad joke retrieval."""
    with requests_mock.Mocker() as m:
        mock_joke = "I tell dad jokes, but I have no kids. I'm a faux pa."
        m.get('https://icanhazdadjoke.com/', json={'joke': mock_joke}, status_code=200)
        
        result = get_dad_joke()
        
        assert result['success'] is True
        assert result['message'] == mock_joke
        assert result['data']['joke'] == mock_joke

def test_get_dad_joke_network_error():
    """Test handling of network errors."""
    with requests_mock.Mocker() as m:
        m.get('https://icanhazdadjoke.com/', exc=requests.exceptions.ConnectTimeout)
        
        result = get_dad_joke()
        
        assert result['success'] is False
        assert 'Error fetching dad joke' in result['message']
        assert result['data'] is None

def test_get_dad_joke_bad_status():
    """Test handling of unexpected API responses."""
    with requests_mock.Mocker() as m:
        m.get('https://icanhazdadjoke.com/', status_code=500)
        
        result = get_dad_joke()
        
        assert result['success'] is False
        assert 'Failed to fetch dad joke' in result['message']
        assert result['data'] is None