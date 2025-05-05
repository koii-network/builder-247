import pytest
import requests
from unittest.mock import patch
from src.dad_joke_client import DadJokeClient

class TestDadJokeClient:
    @pytest.fixture
    def client(self):
        """Create a DadJokeClient instance for testing."""
        return DadJokeClient()

    def test_client_initialization(self, client):
        """Test client initialization with correct base URL and headers."""
        assert client.base_url == "https://icanhazdadjoke.com/"
        assert client.headers == {
            "Accept": "application/json",
            "User-Agent": "Dad Joke API Python Client"
        }

    @patch('requests.get')
    def test_get_random_joke_success(self, mock_get, client):
        """Test successful retrieval of a random joke."""
        mock_response = {
            'id': '123', 
            'joke': 'Test dad joke', 
            'status': 200
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        joke = client.get_random_joke()
        assert joke == 'Test dad joke'
        mock_get.assert_called_once_with(
            client.base_url, 
            headers=client.headers
        )

    @patch('requests.get')
    def test_get_random_joke_failure(self, mock_get, client):
        """Test handling of request failure when getting a random joke."""
        mock_get.side_effect = requests.RequestException('Network error')

        with pytest.raises(requests.RequestException, match='Error fetching dad joke'):
            client.get_random_joke()

    @patch('requests.get')
    def test_get_random_joke_invalid_response(self, mock_get, client):
        """Test handling of invalid joke response."""
        mock_response = {'status': 200}  # Missing 'joke' key
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        with pytest.raises(ValueError, match='Unable to retrieve joke'):
            client.get_random_joke()

    @patch('requests.get')
    def test_search_jokes_success(self, mock_get, client):
        """Test successful search for jokes."""
        mock_response = {
            'results': [
                {'id': '1', 'joke': 'Joke 1'},
                {'id': '2', 'joke': 'Joke 2'}
            ],
            'status': 200
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        jokes = client.search_jokes('test', limit=2)
        assert jokes == ['Joke 1', 'Joke 2']
        mock_get.assert_called_once_with(
            f"{client.base_url}search", 
            params={'term': 'test', 'limit': 2},
            headers=client.headers
        )

    def test_search_jokes_invalid_term(self, client):
        """Test searching with invalid search terms."""
        with pytest.raises(ValueError, match='Search term must be a non-empty string'):
            client.search_jokes('')
        with pytest.raises(ValueError, match='Search term must be a non-empty string'):
            client.search_jokes(None)

    def test_search_jokes_invalid_limit(self, client):
        """Test searching with invalid limit values."""
        with pytest.raises(ValueError, match='Limit must be between 1 and 30'):
            client.search_jokes('test', limit=0)
        with pytest.raises(ValueError, match='Limit must be between 1 and 30'):
            client.search_jokes('test', limit=31)

    @patch('requests.get')
    def test_search_jokes_no_results(self, mock_get, client):
        """Test handling search with no results."""
        mock_response = {'results': [], 'status': 200}
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        jokes = client.search_jokes('nonexistent')
        assert jokes == []

    @patch('requests.get')
    def test_search_jokes_failure(self, mock_get, client):
        """Test handling of request failure during search."""
        mock_get.side_effect = requests.RequestException('Network error')

        with pytest.raises(requests.RequestException, match='Error searching dad jokes'):
            client.search_jokes('test')