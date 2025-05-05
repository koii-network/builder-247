import pytest
import requests
import requests_mock
from prometheus_swarm.clients.dadjoke_client import DadJokeClient

def test_get_random_joke_success():
    """Test successful retrieval of a random dad joke"""
    client = DadJokeClient()
    
    with requests_mock.Mocker() as m:
        mock_joke = {
            "id": "ABC123", 
            "joke": "Why don't scientists trust atoms? Because they make up everything!", 
            "status": 200
        }
        m.get("https://icanhazdadjoke.com/", json=mock_joke)
        
        result = client.get_random_joke()
        
        assert result == mock_joke
        assert m.called
        assert m.call_count == 1

def test_get_random_joke_network_error():
    """Test handling of network errors when fetching a random joke"""
    client = DadJokeClient()
    
    with requests_mock.Mocker() as m:
        m.get("https://icanhazdadjoke.com/", exc=requests.exceptions.ConnectTimeout)
        
        with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
            client.get_random_joke()

def test_search_jokes_success():
    """Test successful search for dad jokes"""
    client = DadJokeClient()
    
    with requests_mock.Mocker() as m:
        mock_search_results = {
            "current_page": 1,
            "limit": 30,
            "results": [
                {"id": "1", "joke": "Joke about science"},
                {"id": "2", "joke": "Another science joke"}
            ],
            "total_jokes": 2,
            "total_pages": 1
        }
        m.get("https://icanhazdadjoke.com/search", json=mock_search_results)
        
        results = client.search_jokes("science")
        
        assert results == mock_search_results['results']
        assert m.called
        assert m.call_count == 1

def test_search_jokes_invalid_input():
    """Test handling of invalid search inputs"""
    client = DadJokeClient()
    
    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        client.search_jokes("")
    
    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        client.search_jokes(None)

def test_search_jokes_network_error():
    """Test handling of network errors during joke search"""
    client = DadJokeClient()
    
    with requests_mock.Mocker() as m:
        m.get("https://icanhazdadjoke.com/search", exc=requests.exceptions.ConnectTimeout)
        
        with pytest.raises(RuntimeError, match="Failed to search dad jokes"):
            client.search_jokes("test")

def test_client_headers():
    """Verify client headers are correctly set"""
    client = DadJokeClient()
    
    assert client.headers['Accept'] == 'application/json'
    assert 'User-Agent' in client.headers
    assert 'Prometheus Swarm Agent' in client.headers['User-Agent']