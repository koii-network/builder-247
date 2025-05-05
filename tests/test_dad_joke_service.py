import pytest
import requests
from unittest.mock import patch, MagicMock
from src.dad_joke_service import DadJokeService

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP Error {self.status_code}")

def test_dad_joke_service_initialization():
    """Test DadJokeService initialization."""
    service = DadJokeService()
    assert service.headers['Accept'] == 'application/json'
    assert service.headers['User-Agent'] == 'DadJokeService/1.0'

@patch('requests.get')
def test_get_random_joke_success(mock_get):
    """Test successful random joke retrieval."""
    mock_joke = {
        'id': '123',
        'joke': 'Why did the scarecrow win an award? Because he was outstanding in his field!',
        'status': 200
    }
    mock_get.return_value = MockResponse(mock_joke)
    
    service = DadJokeService()
    joke = service.get_random_joke()
    
    assert service.validate_joke(joke)
    assert joke['joke'] == mock_joke['joke']
    mock_get.assert_called_once_with(
        service.API_BASE_URL, 
        headers=service.headers
    )

@patch('requests.get')
def test_get_random_joke_network_error(mock_get):
    """Test network error handling when fetching a random joke."""
    mock_get.side_effect = requests.RequestException("Network Error")
    
    service = DadJokeService()
    with pytest.raises(ValueError, match="Failed to fetch dad joke"):
        service.get_random_joke()

@patch('requests.get')
def test_search_jokes_success(mock_get):
    """Test successful joke search."""
    mock_search_results = {
        'results': [
            {
                'id': '1',
                'joke': 'Joke 1',
                'status': 200
            },
            {
                'id': '2',
                'joke': 'Joke 2',
                'status': 200
            }
        ]
    }
    mock_get.return_value = MockResponse(mock_search_results)
    
    service = DadJokeService()
    jokes = service.search_jokes(term='computer', limit=2)
    
    assert len(jokes) == 2
    assert all(service.validate_joke(joke) for joke in jokes)
    mock_get.assert_called_once_with(
        f"{service.API_BASE_URL}search", 
        headers=service.headers, 
        params={'term': 'computer', 'limit': 2}
    )

def test_search_jokes_no_term():
    """Test searching with no term."""
    service = DadJokeService()
    jokes = service.search_jokes()
    assert jokes == []

@patch('requests.get')
def test_search_jokes_network_error(mock_get):
    """Test network error handling during joke search."""
    mock_get.side_effect = requests.RequestException("Network Error")
    
    service = DadJokeService()
    with pytest.raises(ValueError, match="Failed to search dad jokes"):
        service.search_jokes(term='computer')

def test_validate_joke():
    """Test joke validation method."""
    service = DadJokeService()
    
    # Valid joke
    valid_joke = {
        'id': '123',
        'joke': 'A great joke!',
        'status': 200
    }
    assert service.validate_joke(valid_joke) is True
    
    # Invalid jokes
    invalid_jokes = [
        None,  # None
        {},  # Empty dict
        {'id': '123'},  # Missing keys
        {'id': '123', 'joke': '', 'status': 200},  # Empty joke
        {'id': '123', 'joke': 42, 'status': 200}  # Non-string joke
    ]
    
    for invalid_joke in invalid_jokes:
        assert service.validate_joke(invalid_joke) is False