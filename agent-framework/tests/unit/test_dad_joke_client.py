import pytest
import requests
from unittest.mock import patch, Mock
from prometheus_swarm.clients.dad_joke_client import DadJokeClient

class TestDadJokeClient:
    def test_get_random_joke_success(self):
        """
        Test that a random dad joke can be successfully retrieved.
        """
        with patch('requests.get') as mock_get:
            # Create a mock response with a sample joke
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "Why don't scientists trust atoms? Because they make up everything!"
            mock_get.return_value = mock_response

            # Get the joke
            joke = DadJokeClient.get_random_joke()

            # Verify the joke
            assert isinstance(joke, str)
            assert len(joke) > 0
            assert "Why don't scientists trust atoms?" in joke

    def test_get_random_joke_empty_response(self):
        """
        Test handling of an empty joke response.
        """
        with patch('requests.get') as mock_get:
            # Create a mock response with an empty joke
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = ""
            mock_get.return_value = mock_response

            # Verify that an empty response raises a ValueError
            with pytest.raises(requests.RequestException, match="No joke received from the API"):
                DadJokeClient.get_random_joke()

    def test_get_random_joke_network_error(self):
        """
        Test handling of network errors when fetching a joke.
        """
        with patch('requests.get') as mock_get:
            # Simulate a network error
            mock_get.side_effect = requests.RequestException("Network error")

            # Verify that a network error raises a RequestException
            with pytest.raises(requests.RequestException, match="Error fetching dad joke"):
                DadJokeClient.get_random_joke()

    def test_get_random_joke_http_error(self):
        """
        Test handling of HTTP errors when fetching a joke.
        """
        with patch('requests.get') as mock_get:
            # Create a mock response with a bad status code
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            # Verify that an HTTP error raises an exception
            with pytest.raises(requests.RequestException, match="HTTP error 404"):
                DadJokeClient.get_random_joke()