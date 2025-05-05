"""
Test module for Dad Joke Command Handler.
"""

import pytest
import requests_mock
from prometheus_swarm.tools.dad_joke import DadJokeCommandHandler

def test_fetch_random_joke_success():
    """Test successful random joke retrieval."""
    handler = DadJokeCommandHandler()
    
    with requests_mock.Mocker() as m:
        m.get('https://icanhazdadjoke.com/', json={'joke': 'Test dad joke'})
        joke = handler.fetch_random_joke()
        assert joke == 'Test dad joke'

def test_fetch_random_joke_failure():
    """Test joke retrieval when API request fails."""
    handler = DadJokeCommandHandler()
    
    with requests_mock.Mocker() as m:
        m.get('https://icanhazdadjoke.com/', status_code=500)
        joke = handler.fetch_random_joke()
        assert joke is None

def test_fetch_multiple_jokes():
    """Test fetching multiple jokes."""
    handler = DadJokeCommandHandler()
    
    with requests_mock.Mocker() as m:
        m.get('https://icanhazdadjoke.com/', [
            {'json': {'joke': 'Joke 1'}},
            {'json': {'joke': 'Joke 2'}},
            {'json': {'joke': 'Joke 3'}},
            {'json': {'joke': 'Joke 4'}},
            {'json': {'joke': 'Joke 5'}}
        ])
        jokes = handler.fetch_multiple_jokes(count=5)
        assert len(jokes) == 5
        assert all(jokes)

def test_filter_jokes_by_word():
    """Test filtering jokes by keyword."""
    handler = DadJokeCommandHandler()
    
    jokes = [
        "I tell dad jokes, but I don't have kids.",
        "Why don't scientists trust atoms? Because they make up everything!",
        "I'm afraid for the calendar. Its days are numbered."
    ]
    
    filtered_jokes = handler.filter_jokes_by_word(jokes, "dad")
    assert len(filtered_jokes) == 1
    assert filtered_jokes[0] == "I tell dad jokes, but I don't have kids."

def test_get_joke_of_the_day():
    """Test joke of the day feature."""
    handler = DadJokeCommandHandler()
    
    with requests_mock.Mocker() as m:
        m.get('https://icanhazdadjoke.com/', [
            {'json': {'joke': 'Joke 1'}},
            {'json': {'joke': 'Joke 2'}},
            {'json': {'joke': 'Joke 3'}},
            {'json': {'joke': 'Joke 4'}},
            {'json': {'joke': 'Joke 5'}}
        ])
        joke = handler.get_joke_of_the_day()
        assert joke in ['Joke 1', 'Joke 2', 'Joke 3', 'Joke 4', 'Joke 5']

def test_init_with_custom_url():
    """Test initializing with a custom API URL."""
    custom_url = "https://example.com/jokes"
    handler = DadJokeCommandHandler(api_url=custom_url)
    assert handler.api_url == custom_url