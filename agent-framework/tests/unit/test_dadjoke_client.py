"""Unit tests for Dad Joke Client."""

import pytest
import requests_mock
from prometheus_swarm.clients.dadjoke_client import DadJokeClient

def test_get_random_joke():
    """Test retrieving a random dad joke."""
    with requests_mock.Mocker() as m:
        mock_joke = {
            "id": "R7UfaahVfFd",
            "joke": "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "status": 200
        }
        m.get("https://icanhazdadjoke.com/", json=mock_joke)

        client = DadJokeClient()
        joke = client.get_random_joke()

        assert joke == mock_joke
        assert 'joke' in joke
        assert 'id' in joke

def test_rate_joke():
    """Test rating a dad joke."""
    client = DadJokeClient()
    rating_result = client.rate_joke("R7UfaahVfFd", 5)

    assert rating_result['success'] is True
    assert rating_result['joke_id'] == "R7UfaahVfFd"
    assert rating_result['rating'] == 5

def test_joke_retrieval_error():
    """Test error handling during joke retrieval."""
    with requests_mock.Mocker() as m:
        m.get("https://icanhazdadjoke.com/", status_code=500)

        client = DadJokeClient()
        with pytest.raises(requests_mock.requests.RequestException):
            client.get_random_joke()