import pytest
import requests
from unittest.mock import patch, Mock
from prometheus_swarm.clients.dad_joke_client import DadJokeClient

class TestDadJokeClient:
    @pytest.fixture
    def client(self):
        """Create a DadJokeClient instance for testing."""
        return DadJokeClient()

    def test_initialization(self, client):
        """Test client initialization."""
        assert client.base_url == "https://icanhazdadjoke.com/"
        assert client.headers["Accept"] == "application/json"
        assert "Authorization" not in client.headers

    def test_initialization_with_api_key(self):
        """Test client initialization with API key."""
        test_key = "test_api_key"
        client = DadJokeClient(api_key=test_key)
        assert client.headers["Authorization"] == f"Bearer {test_key}"

    @patch('requests.get')
    def test_get_random_joke_success(self, mock_get):
        """Test successful random joke retrieval."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {"joke": "Why don't scientists trust atoms? Because they make up everything!"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = DadJokeClient()
        joke = client.get_random_joke()

        assert joke == "Why don't scientists trust atoms? Because they make up everything!"
        mock_get.assert_called_once_with("https://icanhazdadjoke.com/", headers=client.headers)

    @patch('requests.get')
    def test_get_random_joke_no_joke(self, mock_get):
        """Test getting a joke when no joke is in the response."""
        # Setup mock response with no joke
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = DadJokeClient()
        with pytest.raises(ValueError, match="No joke found in the response"):
            client.get_random_joke()

    @patch('requests.get')
    def test_get_random_joke_request_error(self, mock_get):
        """Test handling of request errors."""
        # Setup mock to raise an exception
        mock_get.side_effect = requests.RequestException("Network error")

        client = DadJokeClient()
        with pytest.raises(requests.RequestException, match="Error fetching dad joke: Network error"):
            client.get_random_joke()

    @patch('requests.get')
    def test_search_jokes_success(self, mock_get):
        """Test successful joke search."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "total_jokes": 2,
            "results": [
                {"joke": "Joke 1"},
                {"joke": "Joke 2"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = DadJokeClient()
        results = client.search_jokes("test", limit=2)

        assert results == {
            "total_jokes": 2,
            "jokes": ["Joke 1", "Joke 2"]
        }
        mock_get.assert_called_once_with(
            "https://icanhazdadjoke.com/search", 
            headers=client.headers, 
            params={"term": "test", "limit": 2}
        )

    def test_search_jokes_empty_term(self):
        """Test searching with an empty term."""
        client = DadJokeClient()
        with pytest.raises(ValueError, match="Search term cannot be empty"):
            client.search_jokes("")

    @patch('requests.get')
    def test_search_jokes_request_error(self, mock_get):
        """Test handling of request errors during search."""
        # Setup mock to raise an exception
        mock_get.side_effect = requests.RequestException("Network error")

        client = DadJokeClient()
        with pytest.raises(requests.RequestException, match="Error searching dad jokes: Network error"):
            client.search_jokes("test")