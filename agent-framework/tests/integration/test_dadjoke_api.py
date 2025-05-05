import pytest
import requests
from prometheus_swarm.clients.dadjoke_client import DadJokeClient

def test_dad_joke_client_initialization():
    """Test that the DadJokeClient can be initialized."""
    client = DadJokeClient()
    assert isinstance(client, DadJokeClient)

def test_get_random_joke():
    """Test retrieving a random dad joke."""
    client = DadJokeClient()
    joke = client.get_random_joke()
    
    assert isinstance(joke, dict)
    assert "id" in joke
    assert "joke" in joke
    assert isinstance(joke["joke"], str)
    assert len(joke["joke"]) > 0

def test_search_jokes():
    """Test searching for dad jokes."""
    client = DadJokeClient()
    search_results = client.search_jokes(term="car")
    
    assert isinstance(search_results, dict)
    assert "results" in search_results
    assert isinstance(search_results["results"], list)
    assert all(isinstance(joke, dict) for joke in search_results["results"])

def test_search_jokes_with_zero_results():
    """Test searching for jokes with a term that returns no results."""
    client = DadJokeClient()
    search_results = client.search_jokes(term="xyzabcnonexistentterm")
    
    assert isinstance(search_results, dict)
    assert "results" in search_results
    assert len(search_results["results"]) == 0

def test_get_random_joke_network_error(mocker):
    """Test handling of network errors when fetching a random joke."""
    client = DadJokeClient()
    
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Network error"))
    
    with pytest.raises(requests.exceptions.RequestException):
        client.get_random_joke()

def test_search_jokes_network_error(mocker):
    """Test handling of network errors when searching jokes."""
    client = DadJokeClient()
    
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Network error"))
    
    with pytest.raises(requests.exceptions.RequestException):
        client.search_jokes(term="test")