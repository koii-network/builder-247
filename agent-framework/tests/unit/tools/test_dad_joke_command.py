import pytest
import requests_mock
from prometheus_swarm.tools.dad_joke_command.implementations import DefaultDadJokeCommandHandler

def test_get_random_joke():
    """Test retrieving a random joke via API."""
    handler = DefaultDadJokeCommandHandler()
    
    with requests_mock.Mocker() as m:
        m.get(handler.api_url, text="Why don't scientists trust atoms? Because they make up everything!")
        joke = handler.get_random_joke()
        assert joke == "Why don't scientists trust atoms? Because they make up everything!"

def test_tell_joke_success():
    """Test telling a joke with basic context."""
    handler = DefaultDadJokeCommandHandler()
    
    with requests_mock.Mocker() as m:
        m.get(handler.api_url, text="Short joke.")
        joke = handler.tell_joke()
        assert joke == "Short joke."

def test_tell_joke_length_filter():
    """Test joke telling with length filter."""
    handler = DefaultDadJokeCommandHandler()
    
    with requests_mock.Mocker() as m:
        m.get(handler.api_url, text="This is a very long joke that exceeds the length filter.")
        with pytest.raises(ValueError, match="Joke too long"):
            handler.tell_joke(context={'filter_length': 10})

def test_rate_joke_success():
    """Test rating a joke."""
    handler = DefaultDadJokeCommandHandler()
    
    joke = "Why did the scarecrow win an award? Because he was outstanding in his field!"
    
    # Rate joke multiple times
    result1 = handler.rate_joke(joke, 4)
    result2 = handler.rate_joke(joke, 5)
    
    assert result1['rating'] == 4
    assert result1['total_ratings'] == 1
    assert result1['average_rating'] == 4.0
    
    assert result2['rating'] == 5
    assert result2['total_ratings'] == 2
    assert result2['average_rating'] == 4.5

def test_rate_joke_invalid_rating():
    """Test rating a joke with invalid rating."""
    handler = DefaultDadJokeCommandHandler()
    
    joke = "Test joke"
    
    with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
        handler.rate_joke(joke, 0)
    
    with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
        handler.rate_joke(joke, 6)

def test_get_random_joke_api_failure():
    """Test handling API failure when fetching joke."""
    handler = DefaultDadJokeCommandHandler()
    
    with requests_mock.Mocker() as m:
        m.get(handler.api_url, status_code=500)
        with pytest.raises(Exception, match="Failed to fetch dad joke"):
            handler.get_random_joke()