import pytest
import requests
from unittest.mock import patch, Mock
from src.dad_joke_service import DadJokeService

class TestDadJokeService:
    def setup_method(self):
        """Setup method to initialize DadJokeService before each test"""
        self.service = DadJokeService()
    
    def test_service_initialization(self):
        """Test that service can be initialized"""
        assert self.service is not None
        assert isinstance(self.service, DadJokeService)
    
    @patch('requests.get')
    def test_get_random_joke_success(self, mock_get):
        """Test successful retrieval of a random joke"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "joke": "Why don't scientists trust atoms? Because they make up everything!",
            "status": 200
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        joke = self.service.get_random_joke()
        
        assert 'id' in joke
        assert 'joke' in joke
        mock_get.assert_called_once_with(
            DadJokeService.BASE_URL, 
            headers=self.service.headers
        )
    
    @patch('requests.get')
    def test_get_random_joke_network_error(self, mock_get):
        """Test handling of network errors"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(ValueError, match="Failed to fetch dad joke"):
            self.service.get_random_joke()
    
    @patch('requests.get')
    def test_get_joke_by_id_success(self, mock_get):
        """Test successful retrieval of a joke by ID"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "abc123",
            "joke": "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "status": 200
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        joke = self.service.get_joke_by_id("abc123")
        
        assert joke['id'] == "abc123"
        assert 'joke' in joke
        mock_get.assert_called_once_with(
            f"{DadJokeService.BASE_URL}j/abc123", 
            headers=self.service.headers
        )
    
    def test_get_joke_by_id_empty_id(self):
        """Test handling of empty joke ID"""
        with pytest.raises(ValueError, match="Joke ID cannot be empty"):
            self.service.get_joke_by_id("")
    
    def test_get_joke_text_success(self):
        """Test extracting joke text from joke dictionary"""
        joke_dict = {"id": "123", "joke": "Test joke", "status": 200}
        
        joke_text = self.service.get_joke_text(joke_dict)
        
        assert joke_text == "Test joke"
    
    def test_get_joke_text_invalid_dict(self):
        """Test handling of invalid joke dictionary"""
        with pytest.raises(ValueError, match="Invalid joke dictionary format"):
            self.service.get_joke_text({"status": 200})