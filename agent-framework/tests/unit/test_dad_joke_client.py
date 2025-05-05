import pytest
import requests
from unittest.mock import patch, Mock
from prometheus_swarm.clients.dad_joke_client import DadJokeClient

class TestDadJokeClient:
    @pytest.fixture
    def client(self):
        return DadJokeClient()

    def test_client_initialization(self):
        client = DadJokeClient()
        assert client.BASE_URL == "https://icanhazdadjoke.com"
        assert client.headers['Accept'] == 'application/json'

    @patch('requests.get')
    def test_get_random_joke_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'joke': 'Why did the scarecrow win an award? Because he was outstanding in his field!'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = DadJokeClient()
        joke = client.get_random_joke()

        assert joke == 'Why did the scarecrow win an award? Because he was outstanding in his field!'
        mock_get.assert_called_once_with(
            'https://icanhazdadjoke.com/',
            headers=client.headers
        )

    @patch('requests.get')
    def test_get_random_joke_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException("Network error")

        client = DadJokeClient()
        with pytest.raises(ValueError, match="Failed to fetch dad joke"):
            client.get_random_joke()

    @patch('requests.get')
    def test_search_jokes_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'joke': 'Why do dads tell bad jokes? Because they love to see you groan!'},
                {'joke': 'Another awesome dad joke'}
            ],
            'total_jokes': 2
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = DadJokeClient()
        result = client.search_jokes('dad')

        assert result == {
            'jokes': [
                'Why do dads tell bad jokes? Because they love to see you groan!',
                'Another awesome dad joke'
            ],
            'total_jokes': 2
        }
        mock_get.assert_called_once_with(
            'https://icanhazdadjoke.com/search',
            params={'term': 'dad', 'limit': 5},
            headers=client.headers
        )

    @patch('requests.get')
    def test_search_jokes_no_results(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [],
            'total_jokes': 0
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = DadJokeClient()
        result = client.search_jokes('unicorn')

        assert result == {'jokes': [], 'total_jokes': 0}

    def test_search_jokes_invalid_input(self, client):
        with pytest.raises(ValueError, match="Search term must not be empty"):
            client.search_jokes('')

        with pytest.raises(ValueError, match="Search term must not be empty"):
            client.search_jokes('   ')