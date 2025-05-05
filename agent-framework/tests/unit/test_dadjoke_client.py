import pytest
import requests
import requests_mock
from prometheus_swarm.clients.dadjoke_client import DadJokeClient

@pytest.fixture
def mock_dadjoke_client():
    return DadJokeClient()

def test_get_random_joke(mock_dadjoke_client):
    with requests_mock.Mocker() as m:
        mock_joke = {
            "id": "abc123", 
            "joke": "Why don't scientists trust atoms? Because they make up everything!", 
            "status": 200
        }
        m.get("https://icanhazdadjoke.com/", json=mock_joke)
        
        result = mock_dadjoke_client.get_random_joke()
        
        assert result == mock_joke
        assert m.call_count == 1

def test_get_joke_by_id(mock_dadjoke_client):
    joke_id = "abc123"
    with requests_mock.Mocker() as m:
        mock_joke = {
            "id": joke_id, 
            "joke": "I told my wife she was drawing her eyebrows too high. She looked surprised.", 
            "status": 200
        }
        m.get(f"https://icanhazdadjoke.com/j/{joke_id}", json=mock_joke)
        
        result = mock_dadjoke_client.get_joke_by_id(joke_id)
        
        assert result == mock_joke
        assert m.call_count == 1

def test_search_jokes(mock_dadjoke_client):
    search_term = "science"
    with requests_mock.Mocker() as m:
        mock_search_result = {
            "current_page": 1,
            "limit": 30,
            "results": [
                {"id": "abc123", "joke": "Science joke 1"},
                {"id": "def456", "joke": "Science joke 2"}
            ],
            "search_term": search_term,
            "total_jokes": 2,
            "total_pages": 1,
            "status": 200
        }
        m.get(f"https://icanhazdadjoke.com/search?term={search_term}&limit=30", json=mock_search_result)
        
        result = mock_dadjoke_client.search_jokes(search_term)
        
        assert result == mock_search_result
        assert m.call_count == 1

def test_get_joke_by_id_empty_id(mock_dadjoke_client):
    with pytest.raises(ValueError, match="Joke ID cannot be empty"):
        mock_dadjoke_client.get_joke_by_id("")

def test_search_jokes_empty_term(mock_dadjoke_client):
    with pytest.raises(ValueError, match="Search term cannot be empty"):
        mock_dadjoke_client.search_jokes("")

def test_search_jokes_invalid_limit(mock_dadjoke_client):
    with pytest.raises(ValueError, match="Limit must be a positive integer"):
        mock_dadjoke_client.search_jokes("science", limit=0)

def test_network_error(mock_dadjoke_client):
    with requests_mock.Mocker() as m:
        m.get("https://icanhazdadjoke.com/", exc=requests.RequestException("Network error"))
        
        with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
            mock_dadjoke_client.get_random_joke()