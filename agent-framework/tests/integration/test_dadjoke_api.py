import pytest
import requests
from prometheus_swarm.clients.dadjoke_client import DadJokeClient

def test_dadjoke_client_initialization():
    """Verify the Dad Joke client initializes correctly"""
    client = DadJokeClient()
    assert client is not None

def test_get_random_joke():
    """Test retrieving a random dad joke"""
    client = DadJokeClient()
    joke = client.get_random_joke()
    
    assert isinstance(joke, dict)
    assert 'id' in joke
    assert 'joke' in joke
    assert 'status' in joke
    assert joke['status'] == 200
    assert isinstance(joke['joke'], str)
    assert len(joke['joke']) > 0

def test_search_jokes():
    """Test searching for dad jokes"""
    client = DadJokeClient()
    search_results = client.search_jokes("computer")
    
    assert isinstance(search_results, dict)
    assert 'results' in search_results
    assert isinstance(search_results['results'], list)
    assert 'total_jokes' in search_results
    assert search_results['total_jokes'] >= 0

def test_search_jokes_empty_term():
    """Test that searching with an empty term raises a ValueError"""
    client = DadJokeClient()
    
    with pytest.raises(ValueError, match="Search term cannot be empty"):
        client.search_jokes("")

def test_joke_api_network_resilience():
    """Verify the client handles network issues gracefully"""
    client = DadJokeClient()
    
    # Temporarily modify the base URL to simulate network failure
    original_url = client.BASE_URL
    client.BASE_URL = "https://non-existent-url.com"
    
    with pytest.raises(RuntimeError, match="Failed to"):
        client.get_random_joke()
    
    # Reset the base URL
    client.BASE_URL = original_url

def test_search_jokes_limit():
    """Test limiting the number of search results"""
    client = DadJokeClient()
    search_results = client.search_jokes("computer", limit=2)
    
    assert len(search_results['results']) <= 2