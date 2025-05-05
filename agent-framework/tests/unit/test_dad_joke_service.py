import pytest
import requests
from unittest.mock import patch, Mock
from prometheus_swarm.services.dad_joke_service import DadJokeService

class TestDadJokeService:
    @pytest.fixture
    def joke_service(self):
        return DadJokeService(cache_size=3)
    
    def test_get_random_joke_success(self, joke_service):
        """Test successful joke retrieval"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'joke': 'Test dad joke'}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            joke = joke_service.get_random_joke()
            assert joke == 'Test dad joke'
    
    def test_get_random_joke_api_error(self, joke_service):
        """Test handling of API errors"""
        with patch('requests.get', side_effect=requests.RequestException):
            joke = joke_service.get_random_joke()
            assert joke is None
    
    def test_joke_caching(self, joke_service):
        """Test joke caching mechanism"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.side_effect = [
                {'joke': 'Joke 1'},
                {'joke': 'Joke 2'},
                {'joke': 'Joke 3'},
                {'joke': 'Joke 4'}
            ]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Fetch jokes to fill cache
            joke_service.get_random_joke()
            joke_service.get_random_joke()
            joke_service.get_random_joke()
            
            cached_jokes = joke_service.get_cached_jokes()
            assert len(cached_jokes) == 3
            assert cached_jokes == ['Joke 1', 'Joke 2', 'Joke 3']
            
            # Fetch 4th joke, which should push out the first joke
            joke_service.get_random_joke()
            
            cached_jokes = joke_service.get_cached_jokes()
            assert len(cached_jokes) == 3
            assert cached_jokes == ['Joke 2', 'Joke 3', 'Joke 4']
    
    def test_clear_cache(self, joke_service):
        """Test cache clearing"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'joke': 'Test joke'}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Add some jokes to cache
            joke_service.get_random_joke()
            joke_service.get_random_joke()
            
            assert len(joke_service.get_cached_jokes()) > 0
            
            # Clear cache
            joke_service.clear_cache()
            
            assert len(joke_service.get_cached_jokes()) == 0