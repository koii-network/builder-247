import pytest
import requests
import requests_mock
from src.dad_joke_service import DadJokeService

@pytest.fixture
def dad_joke_service():
    """Create a DadJokeService instance for testing."""
    return DadJokeService()

def test_init(dad_joke_service):
    """Test initialization of the DadJokeService."""
    assert dad_joke_service is not None
    assert dad_joke_service.BASE_URL == "https://icanhazdadjoke.com/"
    assert dad_joke_service.headers['Accept'] == 'application/json'
    assert dad_joke_service.headers['User-Agent'] == 'Dad Joke Service'

def test_get_random_joke(dad_joke_service):
    """Test getting a random dad joke."""
    with requests_mock.Mocker() as m:
        mock_joke = {
            "id": "abc123",
            "joke": "Why don't scientists trust atoms? Because they make up everything!",
            "status": 200
        }
        m.get(dad_joke_service.BASE_URL, json=mock_joke)
        
        result = dad_joke_service.get_random_joke()
        assert result == mock_joke
        assert 'joke' in result

def test_get_random_joke_network_error(dad_joke_service):
    """Test handling of network errors when fetching a random joke."""
    with requests_mock.Mocker() as m:
        m.get(dad_joke_service.BASE_URL, exc=requests.RequestException)
        
        with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
            dad_joke_service.get_random_joke()

def test_search_jokes_success(dad_joke_service):
    """Test searching for jokes by term."""
    with requests_mock.Mocker() as m:
        mock_results = {
            "results": [
                {
                    "id": "joke1",
                    "joke": "Dad joke about science",
                    "status": 200
                },
                {
                    "id": "joke2",
                    "joke": "Another science dad joke",
                    "status": 200
                }
            ]
        }
        m.get(f"{dad_joke_service.BASE_URL}search", json=mock_results)
        
        results = dad_joke_service.search_jokes("science")
        assert len(results) == 2
        assert all('joke' in joke for joke in results)

def test_search_jokes_invalid_input(dad_joke_service):
    """Test searching with invalid input."""
    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        dad_joke_service.search_jokes("")
    
    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        dad_joke_service.search_jokes(None)

def test_search_jokes_network_error(dad_joke_service):
    """Test handling of network errors when searching jokes."""
    with requests_mock.Mocker() as m:
        m.get(f"{dad_joke_service.BASE_URL}search", exc=requests.RequestException)
        
        with pytest.raises(RuntimeError, match="Failed to search dad jokes"):
            dad_joke_service.search_jokes("science")