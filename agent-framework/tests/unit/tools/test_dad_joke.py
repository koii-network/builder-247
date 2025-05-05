import pytest
import requests
from prometheus_swarm.tools.execute_command.implementations import get_dad_joke

def test_get_dad_joke_successful(mocker):
    """Test fetching a dad joke returns successful result."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"joke": "Why don't scientists trust atoms? Because they make up everything!"}
    
    mocker.patch('requests.get', return_value=mock_response)
    
    result = get_dad_joke()
    
    assert result['success'] is True
    assert 'joke' in result['data']
    assert result['message'] == 'Dad joke fetched successfully'

def test_get_dad_joke_api_error(mocker):
    """Test handling API error."""
    mocker.patch('requests.get', side_effect=requests.RequestException("Connection error"))
    
    result = get_dad_joke()
    
    assert result['success'] is False
    assert 'error' in result['data']
    assert 'Connection error' in result['message']

def test_get_dad_joke_bad_status_code(mocker):
    """Test handling bad status code from API."""
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    
    mocker.patch('requests.get', return_value=mock_response)
    
    result = get_dad_joke()
    
    assert result['success'] is False
    assert result['data']['status_code'] == 500
    assert 'Failed to fetch dad joke' in result['message']