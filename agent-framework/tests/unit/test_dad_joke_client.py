import pytest
import requests
import requests_mock
from prometheus_swarm.clients.dad_joke_client import DadJokeClient

@pytest.fixture
def dad_joke_client():
    """Fixture to create a DadJokeClient instance"""
    return DadJokeClient()

def test_get_random_joke(dad_joke_client):
    """Test retrieving a random dad joke"""
    with requests_mock.Mocker() as m:
        mock_joke = {
            "id": "abc123", 
            "joke": "Why don't scientists trust atoms? Because they make up everything!",
            "status": 200
        }
        m.get(
            "https://icanhazdadjoke.com", 
            json=mock_joke,
            headers={"Content-Type": "application/json"}
        )
        
        result = dad_joke_client.get_random_joke()
        
        assert result == mock_joke
        assert m.called
        assert m.call_count == 1

def test_search_jokes(dad_joke_client):
    """Test searching for dad jokes"""
    with requests_mock.Mocker() as m:
        mock_search_results = {
            "current_page": 1,
            "limit": 30,
            "next_page": 2,
            "previous_page": 0,
            "results": [
                {
                    "id": "joke1", 
                    "joke": "A funny science joke", 
                    "status": 200
                },
                {
                    "id": "joke2", 
                    "joke": "Another science joke", 
                    "status": 200
                }
            ],
            "search_term": "science",
            "total_jokes": 100,
            "total_pages": 4
        }
        m.get(
            "https://icanhazdadjoke.com/search?term=science&limit=30", 
            json=mock_search_results,
            headers={"Content-Type": "application/json"}
        )
        
        result = dad_joke_client.search_jokes("science")
        
        assert result == mock_search_results
        assert m.called
        assert m.call_count == 1

def test_random_joke_api_error(dad_joke_client):
    """Test handling of API errors when getting a random joke"""
    with requests_mock.Mocker() as m:
        m.get(
            "https://icanhazdadjoke.com", 
            status_code=500,
            reason="Internal Server Error"
        )
        
        with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
            dad_joke_client.get_random_joke()

def test_search_jokes_api_error(dad_joke_client):
    """Test handling of API errors when searching jokes"""
    with requests_mock.Mocker() as m:
        m.get(
            "https://icanhazdadjoke.com/search", 
            status_code=400,
            reason="Bad Request"
        )
        
        with pytest.raises(RuntimeError, match="Failed to search dad jokes"):
            dad_joke_client.search_jokes("test")

def test_search_jokes_custom_limit(dad_joke_client):
    """Test searching with a custom limit"""
    with requests_mock.Mocker() as m:
        m.get(
            "https://icanhazdadjoke.com/search?term=programming&limit=10", 
            json={"results": [], "total_jokes": 0},
            headers={"Content-Type": "application/json"}
        )
        
        result = dad_joke_client.search_jokes("programming", limit=10)
        
        assert result == {"results": [], "total_jokes": 0}
        assert m.called
        assert m.call_count == 1

def test_headers():
    """Test that the client sets the correct headers"""
    client = DadJokeClient()
    assert client.headers["Accept"] == "application/json"
    assert client.headers["User-Agent"] == "PrometheusSwarm/1.0"