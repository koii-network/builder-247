import pytest
import requests
from unittest.mock import patch, Mock
from src.dad_joke_service import DadJokeService

class TestDadJokeService:
    @pytest.fixture
    def mock_service(self):
        """Create a DadJokeService instance for testing."""
        return DadJokeService()

    def test_get_random_joke_success(self, mock_service):
        """Test successful retrieval of a random joke."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'id': '123', 
                'joke': 'A hilarious dad joke', 
                'status': 200
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            joke = mock_service.get_random_joke()
            assert 'id' in joke
            assert 'joke' in joke

    def test_get_random_joke_api_error(self, mock_service):
        """Test handling of API request failure."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("API Error")

            with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
                mock_service.get_random_joke()

    def test_get_joke_by_id_success(self, mock_service):
        """Test successful retrieval of a joke by ID."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'id': 'abc123', 
                'joke': 'A specific dad joke', 
                'status': 200
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            joke = mock_service.get_joke_by_id('abc123')
            assert joke['id'] == 'abc123'

    def test_get_joke_by_id_invalid_input(self, mock_service):
        """Test invalid joke ID input."""
        with pytest.raises(ValueError, match="Invalid joke ID"):
            mock_service.get_joke_by_id(None)
        with pytest.raises(ValueError, match="Invalid joke ID"):
            mock_service.get_joke_by_id(123)

    def test_search_jokes_success(self, mock_service):
        """Test successful joke search."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'results': [
                    {'id': '1', 'joke': 'First joke'},
                    {'id': '2', 'joke': 'Second joke'}
                ],
                'status': 200
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            results = mock_service.search_jokes('funny')
            assert len(results) == 2
            assert all('id' in joke and 'joke' in joke for joke in results)

    def test_search_jokes_invalid_input(self, mock_service):
        """Test invalid search term input."""
        with pytest.raises(ValueError, match="Invalid search term"):
            mock_service.search_jokes(None)
        with pytest.raises(ValueError, match="Invalid search term"):
            mock_service.search_jokes('')

    def test_search_jokes_api_error(self, mock_service):
        """Test handling of API request failure during search."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Search Error")

            with pytest.raises(RuntimeError, match="Failed to search dad jokes"):
                mock_service.search_jokes('test')

    def test_custom_api_url(self):
        """Test ability to use a custom API URL."""
        custom_url = 'https://custom-dad-jokes.com/'
        service = DadJokeService(custom_url)
        assert service.api_url == custom_url