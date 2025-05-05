import pytest
import requests
from unittest.mock import patch, Mock
from prometheus_swarm.clients.dad_joke_client import DadJokeClient

class TestDadJokeClient:
    @pytest.fixture
    def dad_joke_client(self):
        """Create a DadJokeClient instance for testing"""
        return DadJokeClient()

    def test_get_random_joke_success(self, dad_joke_client):
        """Test successful retrieval of a random joke"""
        mock_response = Mock()
        mock_response.json.return_value = {"joke": "Why don't scientists trust atoms? Because they make up everything!"}
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response) as mock_get:
            joke = dad_joke_client.get_random_joke()
            assert joke == "Why don't scientists trust atoms? Because they make up everything!"
            mock_get.assert_called_once_with(
                DadJokeClient.BASE_URL, 
                headers=dad_joke_client.headers, 
                timeout=dad_joke_client.timeout
            )

    def test_get_random_joke_network_error(self, dad_joke_client):
        """Test handling of network errors when fetching a random joke"""
        with patch('requests.get', side_effect=requests.RequestException):
            joke = dad_joke_client.get_random_joke()
            assert joke is None

    def test_search_jokes_success(self, dad_joke_client):
        """Test successful search for jokes"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"joke": "Programmer joke 1"},
                {"joke": "Programmer joke 2"}
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response) as mock_get:
            jokes = dad_joke_client.search_jokes("programmer")
            assert jokes == ["Programmer joke 1", "Programmer joke 2"]
            mock_get.assert_called_once_with(
                f"{DadJokeClient.BASE_URL}/search", 
                params={"term": "programmer", "limit": 5},
                headers=dad_joke_client.headers,
                timeout=dad_joke_client.timeout
            )

    def test_search_jokes_network_error(self, dad_joke_client):
        """Test handling of network errors during joke search"""
        with patch('requests.get', side_effect=requests.RequestException):
            jokes = dad_joke_client.search_jokes("programmer")
            assert jokes == []

    def test_search_jokes_invalid_input(self, dad_joke_client):
        """Test handling of invalid search inputs"""
        assert dad_joke_client.search_jokes("") == []
        assert dad_joke_client.search_jokes(None) == []
        assert dad_joke_client.search_jokes(123) == []

    def test_search_jokes_no_results(self, dad_joke_client):
        """Test handling of empty search results"""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()

        with patch('requests.get', return_value=mock_response):
            jokes = dad_joke_client.search_jokes("xyzabc")
            assert jokes == []