import pytest
import requests
from unittest.mock import patch, Mock
from prometheus_swarm.clients.dad_joke_client import DadJokeClient

class TestDadJokeClient:
    @pytest.fixture
    def mock_requests_get(self):
        with patch('requests.get') as mock_get:
            yield mock_get
    
    def test_get_random_joke_success(self, mock_requests_get):
        # Setup mock response for a successful random joke
        mock_response = Mock()
        mock_response.json.return_value = {'joke': 'Why did the scarecrow win an award? Because he was outstanding in his field!'}
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        
        client = DadJokeClient()
        joke = client.get_random_joke()
        
        assert joke == 'Why did the scarecrow win an award? Because he was outstanding in his field!'
        mock_requests_get.assert_called_once_with(
            'https://icanhazdadjoke.com/', 
            headers={
                'Accept': 'application/json', 
                'User-Agent': 'Dad Joke API Client'
            }
        )
    
    def test_get_random_joke_no_joke_in_response(self, mock_requests_get):
        # Setup mock response with no joke
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        
        client = DadJokeClient()
        
        with pytest.raises(ValueError, match="No joke found in the API response"):
            client.get_random_joke()
    
    def test_get_random_joke_request_exception(self, mock_requests_get):
        # Simulate a request failure
        mock_requests_get.side_effect = requests.RequestException("Network error")
        
        client = DadJokeClient()
        
        with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
            client.get_random_joke()
    
    def test_search_jokes_success(self, mock_requests_get):
        # Setup mock response for joke search
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'joke': 'Dad joke 1'},
                {'joke': 'Dad joke 2'}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        
        client = DadJokeClient()
        jokes = client.search_jokes('dad')
        
        assert jokes == ['Dad joke 1', 'Dad joke 2']
        mock_requests_get.assert_called_once_with(
            'https://icanhazdadjoke.com/search', 
            headers={
                'Accept': 'application/json', 
                'User-Agent': 'Dad Joke API Client'
            },
            params={'term': 'dad'}
        )
    
    def test_search_jokes_empty_term(self):
        client = DadJokeClient()
        
        with pytest.raises(ValueError, match="Search term must not be empty"):
            client.search_jokes('')
    
    def test_search_jokes_request_exception(self, mock_requests_get):
        # Simulate a request failure during search
        mock_requests_get.side_effect = requests.RequestException("Network error")
        
        client = DadJokeClient()
        
        with pytest.raises(RuntimeError, match="Failed to search dad jokes"):
            client.search_jokes('dad')
    
    def test_custom_api_url(self):
        # Test custom API URL
        custom_url = 'https://custom-dad-jokes.com/'
        client = DadJokeClient(api_url=custom_url)
        
        assert client.base_url == custom_url