import pytest
import requests
import requests_mock
from prometheus_swarm.clients.dadjoke_client import DadJokeClient

def test_get_random_joke():
    """Test getting a random dad joke."""
    with requests_mock.Mocker() as m:
        # Mock the API response
        mock_joke = {"joke": "Why don't scientists trust atoms? Because they make up everything!"}
        m.get('https://icanhazdadjoke.com/', json=mock_joke)
        
        client = DadJokeClient()
        joke = client.get_random_joke()
        
        assert joke == mock_joke['joke']
        assert m.call_count == 1

def test_get_random_joke_network_error():
    """Test handling network errors when fetching a random joke."""
    with requests_mock.Mocker() as m:
        # Simulate a network error
        m.get('https://icanhazdadjoke.com/', exc=requests.ConnectionError)
        
        client = DadJokeClient()
        with pytest.raises(requests.RequestException):
            client.get_random_joke()

def test_get_random_joke_invalid_response():
    """Test handling invalid API response."""
    with requests_mock.Mocker() as m:
        # Mock an invalid response without a joke
        m.get('https://icanhazdadjoke.com/', json={})
        
        client = DadJokeClient()
        with pytest.raises(ValueError, match="No joke found in response"):
            client.get_random_joke()

def test_get_joke_by_id():
    """Test getting a specific joke by ID."""
    joke_id = "abc123"
    with requests_mock.Mocker() as m:
        # Mock the API response for a specific joke
        mock_joke = {"joke": "I told my wife she was drawing her eyebrows too high. She looked surprised."}
        m.get(f'https://icanhazdadjoke.com/j/{joke_id}', json=mock_joke)
        
        client = DadJokeClient()
        joke = client.get_joke_by_id(joke_id)
        
        assert joke == mock_joke['joke']
        assert m.call_count == 1

def test_get_joke_by_id_not_found():
    """Test handling non-existent joke ID."""
    joke_id = "nonexistent"
    with requests_mock.Mocker() as m:
        # Simulate a 404 response
        m.get(f'https://icanhazdadjoke.com/j/{joke_id}', status_code=404, json={})
        
        client = DadJokeClient()
        with pytest.raises(requests.RequestException):
            client.get_joke_by_id(joke_id)

def test_get_joke_by_id_invalid_response():
    """Test handling invalid response for a specific joke ID."""
    joke_id = "invalid"
    with requests_mock.Mocker() as m:
        # Mock an invalid response without a joke
        m.get(f'https://icanhazdadjoke.com/j/{joke_id}', json={})
        
        client = DadJokeClient()
        with pytest.raises(ValueError, match=f"No joke found for ID: {joke_id}"):
            client.get_joke_by_id(joke_id)