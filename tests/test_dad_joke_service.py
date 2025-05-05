import pytest
import requests
from unittest.mock import Mock, patch
from src.dad_joke_service import DadJokeService

@pytest.fixture
def mock_joke_response():
    return {
        "id": "test_joke_id",
        "joke": "Why don't scientists trust atoms? Because they make up everything!"
    }

@pytest.fixture
def dad_joke_service():
    return DadJokeService()

def test_get_random_joke(dad_joke_service, mock_joke_response):
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_joke_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        joke = dad_joke_service.get_random_joke()
        assert joke == mock_joke_response
        mock_get.assert_called_once_with(
            "https://icanhazdadjoke.com/", 
            headers={
                'Accept': 'application/json', 
                'User-Agent': 'Dad Joke Service'
            }
        )

def test_get_joke_by_id(dad_joke_service, mock_joke_response):
    joke_id = "test_joke_id"
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_joke_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        joke = dad_joke_service.get_joke_by_id(joke_id)
        assert joke == mock_joke_response
        mock_get.assert_called_once_with(
            f"https://icanhazdadjoke.com/j/{joke_id}", 
            headers={
                'Accept': 'application/json', 
                'User-Agent': 'Dad Joke Service'
            }
        )

def test_get_joke_by_id_not_found(dad_joke_service):
    joke_id = "non_existent_id"
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="No joke found with ID"):
            dad_joke_service.get_joke_by_id(joke_id)

def test_search_jokes(dad_joke_service):
    search_term = "science"
    mock_search_result = {
        "results": [
            {"id": "1", "joke": "Science joke 1"},
            {"id": "2", "joke": "Science joke 2"}
        ]
    }
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_search_result
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        jokes = dad_joke_service.search_jokes(search_term)
        assert jokes == mock_search_result['results']
        mock_get.assert_called_once_with(
            "https://icanhazdadjoke.com/search", 
            params={'term': search_term, 'limit': 30},
            headers={
                'Accept': 'application/json', 
                'User-Agent': 'Dad Joke Service'
            }
        )

def test_search_jokes_invalid_term(dad_joke_service):
    with pytest.raises(ValueError, match="Search term must be at least 2 characters long"):
        dad_joke_service.search_jokes("a")

def test_get_random_joke_request_error(dad_joke_service):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")

        with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
            dad_joke_service.get_random_joke()