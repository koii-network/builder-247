import pytest
import requests
from src.dad_joke_client import DadJokeClient

class MockResponse:
    """Mock response class for testing"""
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(f"HTTP Error {self.status_code}")

def test_get_random_joke(monkeypatch):
    """Test retrieving a random dad joke"""
    def mock_get(*args, **kwargs):
        return MockResponse({
            "id": "abc123",
            "joke": "Test dad joke",
            "status": 200
        })
    
    monkeypatch.setattr(requests, 'get', mock_get)
    
    client = DadJokeClient()
    joke = client.get_random_joke()
    
    assert joke == "Test dad joke"

def test_get_random_joke_api_error(monkeypatch):
    """Test handling API errors when fetching a random joke"""
    def mock_get(*args, **kwargs):
        raise requests.RequestException("API Error")
    
    monkeypatch.setattr(requests, 'get', mock_get)
    
    client = DadJokeClient()
    with pytest.raises(requests.RequestException):
        client.get_random_joke()

def test_search_jokes(monkeypatch):
    """Test searching for jokes with a specific term"""
    def mock_get(*args, **kwargs):
        return MockResponse({
            "results": [
                {"joke": "First test joke"},
                {"joke": "Second test joke"}
            ],
            "status": 200
        })
    
    monkeypatch.setattr(requests, 'get', mock_get)
    
    client = DadJokeClient()
    jokes = client.search_jokes("test", limit=2)
    
    assert len(jokes) == 2
    assert "First test joke" in jokes
    assert "Second test joke" in jokes

def test_search_jokes_invalid_term():
    """Test searching with an invalid term"""
    client = DadJokeClient()
    
    with pytest.raises(ValueError):
        client.search_jokes("")
    
    with pytest.raises(ValueError):
        client.search_jokes(None)

def test_search_jokes_no_results(monkeypatch):
    """Test searching when no jokes are found"""
    def mock_get(*args, **kwargs):
        return MockResponse({
            "results": [],
            "status": 200
        })
    
    monkeypatch.setattr(requests, 'get', mock_get)
    
    client = DadJokeClient()
    jokes = client.search_jokes("nonexistent")
    
    assert jokes == []