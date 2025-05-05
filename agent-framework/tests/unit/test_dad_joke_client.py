import pytest
import requests
from unittest.mock import patch, MagicMock
from prometheus_swarm.clients.dad_joke_client import DadJokeClient
from prometheus_swarm.utils.errors import APIClientError

class TestDadJokeClient:
    @pytest.fixture
    def client(self):
        return DadJokeClient()

    def test_get_random_joke_success(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {'joke': 'Why do programmers prefer dark mode? Light attracts bugs!'}
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response) as mock_get:
            joke = client.get_random_joke()
            assert joke == 'Why do programmers prefer dark mode? Light attracts bugs!'
            mock_get.assert_called_once_with(
                'https://icanhazdadjoke.com/',
                headers=client.headers
            )

    def test_get_random_joke_no_joke_found(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            joke = client.get_random_joke()
            assert joke == 'No joke found'

    def test_get_random_joke_api_error(self, client):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException('Network error')
            
            with pytest.raises(APIClientError, match='Failed to fetch dad joke: Network error'):
                client.get_random_joke()

    def test_search_jokes_success(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [
                {'joke': 'Programmer joke 1'},
                {'joke': 'Programmer joke 2'}
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response) as mock_get:
            jokes = client.search_jokes('programmer')
            assert jokes == ['Programmer joke 1', 'Programmer joke 2']
            mock_get.assert_called_once_with(
                'https://icanhazdadjoke.com/search',
                params={'term': 'programmer', 'limit': 5},
                headers=client.headers
            )

    def test_search_jokes_no_results(self, client):
        mock_response = MagicMock()
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            jokes = client.search_jokes('unicorn')
            assert jokes == []

    def test_search_jokes_api_error(self, client):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException('Network error')
            
            with pytest.raises(APIClientError, match='Failed to search dad jokes: Network error'):
                client.search_jokes('programmer')