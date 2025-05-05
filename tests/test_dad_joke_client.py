import pytest
import requests
from unittest.mock import patch
from src.dad_joke_client import DadJokeClient

class TestDadJokeClient:
    @pytest.fixture
    def mock_client(self):
        """Create a DadJokeClient instance for testing."""
        return DadJokeClient()

    def test_get_random_joke_success(self, mock_client):
        """Test successful random joke retrieval."""
        with patch('requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.json.return_value = {
                'id': '123',
                'joke': 'A funny dad joke',
                'status': 200
            }
            mock_response.raise_for_status.return_value = None

            joke = mock_client.get_random_joke()
            assert 'joke' in joke
            assert joke['joke'] == 'A funny dad joke'

    def test_get_random_joke_network_error(self, mock_client):
        """Test network error handling."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            with pytest.raises(requests.RequestException, match="Error fetching joke"):
                mock_client.get_random_joke()

    def test_get_random_joke_invalid_response(self, mock_client):
        """Test handling of invalid joke response."""
        with patch('requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.json.return_value = {}
            mock_response.raise_for_status.return_value = None

            with pytest.raises(ValueError, match="Invalid joke response"):
                mock_client.get_random_joke()

    def test_search_jokes_success(self, mock_client):
        """Test successful joke search."""
        with patch('requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.json.return_value = {
                'results': [
                    {'id': '1', 'joke': 'Joke 1'},
                    {'id': '2', 'joke': 'Joke 2'}
                ]
            }
            mock_response.raise_for_status.return_value = None

            results = mock_client.search_jokes('programming')
            assert len(results) == 2
            assert results[0]['joke'] == 'Joke 1'

    def test_search_jokes_empty_term(self, mock_client):
        """Test searching with an empty term."""
        with pytest.raises(ValueError, match="Search term cannot be empty"):
            mock_client.search_jokes('')

    def test_search_jokes_invalid_limit(self, mock_client):
        """Test searching with an invalid limit."""
        with pytest.raises(ValueError, match="Limit must be at least 1"):
            mock_client.search_jokes('test', limit=0)

    def test_search_jokes_network_error(self, mock_client):
        """Test network error during joke search."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            with pytest.raises(requests.RequestException, match="Error searching jokes"):
                mock_client.search_jokes('programming')

    def test_search_jokes_invalid_response(self, mock_client):
        """Test handling of invalid search response."""
        with patch('requests.get') as mock_get:
            mock_response = mock_get.return_value
            mock_response.json.return_value = {}
            mock_response.raise_for_status.return_value = None

            with pytest.raises(ValueError, match="Invalid search response"):
                mock_client.search_jokes('programming')