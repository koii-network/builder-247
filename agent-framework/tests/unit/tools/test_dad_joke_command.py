import pytest
import requests
from unittest.mock import patch
from prometheus_swarm.tools.dad_joke_operations import DadJokeCommandHandler

class TestDadJokeCommandHandler:
    @pytest.fixture
    def dad_joke_handler(self):
        return DadJokeCommandHandler()

    def test_get_dad_joke_success(self, dad_joke_handler):
        """Test successful dad joke retrieval from API."""
        mock_response = {
            'joke': 'Test Dad Joke',
            'id': '123456'
        }
        
        with patch('requests.get') as mock_get:
            mock_response_obj = mock_get.return_value
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            
            result = dad_joke_handler.get_dad_joke()
            
            assert 'joke' in result
            assert 'id' in result
            assert result['joke'] == 'Test Dad Joke'
            assert result['id'] == '123456'

    def test_get_dad_joke_api_failure(self, dad_joke_handler):
        """Test fallback to local jokes when API fails."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException('API Error')
            
            result = dad_joke_handler.get_dad_joke()
            
            assert 'joke' in result
            assert 'error' in result
            assert len(result['joke']) > 0
            assert 'API Error' in result['error']

    def test_dad_joke_consistency(self, dad_joke_handler):
        """Ensure dad joke always returns a dictionary with expected keys."""
        result1 = dad_joke_handler.get_dad_joke()
        result2 = dad_joke_handler.get_dad_joke()
        
        assert 'joke' in result1
        assert 'id' in result1
        assert 'joke' in result2
        assert 'id' in result2
        assert isinstance(result1['joke'], str)
        assert len(result1['joke']) > 0