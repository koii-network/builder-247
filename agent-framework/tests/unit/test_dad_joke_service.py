import pytest
import requests
from unittest.mock import patch
from prometheus_swarm.services.dad_joke_service import DadJokeService

def test_dad_joke_service_initialization():
    """Test initialization of DadJokeService."""
    service = DadJokeService()
    assert service.api_url == "https://icanhazdadjoke.com/"
    assert service.headers["Accept"] == "application/json"

@patch('requests.get')
def test_get_random_joke_success(mock_get):
    """Test successful retrieval of a random joke."""
    mock_response = mock_get.return_value
    mock_response.json.return_value = {
        "id": "abc123", 
        "joke": "Test dad joke", 
        "status": 200
    }
    mock_response.raise_for_status.return_value = None

    service = DadJokeService()
    joke = service.get_random_joke()

    assert joke is not None
    assert "joke" in joke
    mock_get.assert_called_once()

@patch('requests.get')
def test_get_random_joke_failure(mock_get):
    """Test handling of joke retrieval failure."""
    mock_get.side_effect = requests.RequestException()

    service = DadJokeService()
    joke = service.get_random_joke()

    assert joke is None

def test_generate_custom_joke():
    """Test generation of a custom dad joke."""
    service = DadJokeService()
    
    # Test with default topics
    joke1 = service.generate_custom_joke()
    assert joke1 is not None
    assert len(joke1) > 0

    # Test with custom topics
    joke2 = service.generate_custom_joke(["robot", "developer"])
    assert joke2 is not None
    assert len(joke2) > 0
    assert any(topic in joke2 for topic in ["robot", "developer"])

def test_validate_joke():
    """Test joke validation."""
    service = DadJokeService()

    # Test valid jokes
    valid_jokes = [
        "Why did the chicken cross the road?",
        "A short and sweet joke",
        "Dad jokes are the best!"
    ]
    for joke in valid_jokes:
        assert service.validate_joke(joke) is True

    # Test invalid jokes
    invalid_jokes = [
        "",  # Empty joke
        "A" * 300,  # Too long
        "This joke contains a bad word"
    ]
    for joke in invalid_jokes:
        assert service.validate_joke(joke) is False