import pytest
import requests
from unittest.mock import Mock, patch
from src.dad_joke_service import DadJokeService

class TestDadJokeService:
    @pytest.fixture
    def mock_requests_get(self):
        """
        Fixture to mock requests.get for consistent testing
        """
        with patch('requests.get') as mock_get:
            yield mock_get

    def test_initialization(self):
        """
        Test service initialization
        """
        service = DadJokeService()
        assert service is not None
        assert service.BASE_URL == "https://icanhazdadjoke.com/"
        assert service.headers == {
            "Accept": "application/json",
            "User-Agent": "DadJokeService/1.0"
        }

    def test_get_random_joke_success(self, mock_requests_get):
        """
        Test successful random joke retrieval
        """
        # Prepare mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "abc123",
            "joke": "Why don't scientists trust atoms? Because they make up everything!",
            "status": 200
        }
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        service = DadJokeService()
        joke = service.get_random_joke()

        assert joke['joke'] is not None
        assert 'id' in joke
        mock_requests_get.assert_called_once_with(
            "https://icanhazdadjoke.com/", 
            headers=service.headers
        )

    def test_get_random_joke_network_error(self, mock_requests_get):
        """
        Test handling of network errors
        """
        mock_requests_get.side_effect = requests.RequestException("Network error")

        service = DadJokeService()
        with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
            service.get_random_joke()

    def test_search_jokes_success(self, mock_requests_get):
        """
        Test successful joke search
        """
        # Prepare mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": "1", "joke": "Joke 1"},
                {"id": "2", "joke": "Joke 2"}
            ],
            "status": 200
        }
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        service = DadJokeService()
        results = service.search_jokes("science")

        assert len(results) == 2
        mock_requests_get.assert_called_once_with(
            "https://icanhazdadjoke.com/search", 
            headers=service.headers, 
            params={"term": "science", "limit": 5}
        )

    def test_search_jokes_invalid_term(self):
        """
        Test handling of invalid search terms
        """
        service = DadJokeService()
        
        with pytest.raises(ValueError, match="Search term must be a non-empty string"):
            service.search_jokes("")
        
        with pytest.raises(ValueError, match="Search term must be a non-empty string"):
            service.search_jokes(None)

    def test_search_jokes_no_results(self, mock_requests_get):
        """
        Test handling of empty search results
        """
        # Prepare mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [],
            "status": 200
        }
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        service = DadJokeService()
        results = service.search_jokes("nonexistent")

        assert len(results) == 0

    def test_search_jokes_network_error(self, mock_requests_get):
        """
        Test handling of network errors during search
        """
        mock_requests_get.side_effect = requests.RequestException("Network error")

        service = DadJokeService()
        with pytest.raises(RuntimeError, match="Failed to search dad jokes"):
            service.search_jokes("test")