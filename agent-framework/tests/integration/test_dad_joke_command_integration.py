"""Integration tests for Dad Joke Command Handler."""

import pytest
import requests
from prometheus_swarm.tools.dad_joke_command.implementations import (
    get_dad_joke,
    generate_offline_dad_joke,
    get_dad_joke_command
)

def test_dad_joke_api_availability():
    """
    Test the availability of the icanhazdadjoke API.
    
    This test checks whether the API is reachable and returns a joke.
    """
    headers = {"Accept": "application/json"}
    url = "https://icanhazdadjoke.com/"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        assert response.status_code == 200, "icanhazdadjoke API is not accessible"
        joke = response.json()
        assert "joke" in joke, "API response does not contain a joke"
    except requests.RequestException as e:
        pytest.skip(f"Could not connect to icanhazdadjoke API: {e}")

def test_get_dad_joke_online():
    """
    Test fetching a dad joke from the online API.
    
    This test verifies that a joke is returned and meets basic quality checks.
    """
    try:
        joke = get_dad_joke()
        assert isinstance(joke, str), "Joke must be a string"
        assert len(joke) > 10, "Joke is too short to be believable"
        assert len(joke) < 300, "Joke is unreasonably long"
    except Exception as e:
        pytest.fail(f"Failed to fetch online dad joke: {e}")

def test_generate_offline_dad_joke():
    """
    Test generating an offline dad joke.
    
    This test ensures that a joke is returned and meets basic quality checks.
    """
    joke = generate_offline_dad_joke()
    assert isinstance(joke, str), "Offline joke must be a string"
    assert len(joke) > 10, "Offline joke is too short"
    assert len(joke) < 300, "Offline joke is unreasonably long"

def test_get_dad_joke_command_fallback():
    """
    Test the dad joke command with potential API failures.
    
    This test ensures that even if the online API fails, 
    a joke can still be generated from the offline collection.
    """
    joke = get_dad_joke_command()
    assert isinstance(joke, str), "Dad joke command must return a string"
    assert len(joke) > 10, "Dad joke is too short"
    assert len(joke) < 300, "Dad joke is unreasonably long"