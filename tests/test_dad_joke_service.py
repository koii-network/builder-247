import pytest
import requests
from unittest.mock import patch, MagicMock
from src.dad_joke_service import DadJokeService

class TestDadJokeService:
    def setup_method(self):
        """Setup a fresh DadJokeService instance for each test."""
        self.service = DadJokeService()
    
    def test_init(self):
        """Test service initialization."""
        assert len(self.service.local_jokes) > 0
        assert isinstance(self.service.local_jokes, list)
    
    def test_get_random_local_joke(self):
        """Test getting a random local joke."""
        joke = self.service.get_random_joke(source='local')
        assert joke in self.service.local_jokes
    
    def test_invalid_source_raises_error(self):
        """Test that an invalid source raises a ValueError."""
        with pytest.raises(ValueError, match="Invalid joke source"):
            self.service.get_random_joke(source='invalid')
    
    @patch('requests.get')
    def test_get_random_api_joke(self, mock_get):
        """Test getting a random joke from the API."""
        mock_response = MagicMock()
        mock_response.text = "Test API joke"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        joke = self.service.get_random_joke(source='api')
        assert joke == "Test API joke"
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_api_failure_raises_error(self, mock_get):
        """Test that API request failure raises a RuntimeError."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(RuntimeError, match="Failed to fetch joke"):
            self.service.get_random_joke(source='api')
    
    def test_add_local_joke(self):
        """Test adding a new local joke."""
        initial_joke_count = len(self.service.local_jokes)
        new_joke = "Why did the scarecrow win an award? Because he was outstanding in his field!"
        
        self.service.add_local_joke(new_joke)
        
        assert len(self.service.local_jokes) == initial_joke_count + 1
        assert new_joke in self.service.local_jokes
    
    def test_add_duplicate_joke_ignored(self):
        """Test that duplicate jokes are not added."""
        initial_jokes = self.service.local_jokes.copy()
        first_joke = initial_jokes[0]
        
        self.service.add_local_joke(first_joke)
        
        assert self.service.local_jokes == initial_jokes
    
    def test_add_empty_joke_raises_error(self):
        """Test that empty jokes are not allowed."""
        with pytest.raises(ValueError, match="Joke cannot be empty"):
            self.service.add_local_joke("")
        
        with pytest.raises(ValueError, match="Joke cannot be empty"):
            self.service.add_local_joke("   ")
    
    def test_add_non_string_joke_raises_error(self):
        """Test that non-string jokes are not allowed."""
        with pytest.raises(ValueError, match="Joke must be a string"):
            self.service.add_local_joke(123)
    
    def test_get_local_jokes(self):
        """Test retrieving local jokes."""
        local_jokes = self.service.get_local_jokes()
        
        assert isinstance(local_jokes, list)
        assert local_jokes == self.service.local_jokes
        
        # Ensure it's a copy, not the original list
        local_jokes.append("New joke")
        assert "New joke" not in self.service.local_jokes
    
    @patch('requests.get')
    def test_mixed_source_joke(self, mock_get):
        """Test getting a joke from mixed sources."""
        mock_response = MagicMock()
        mock_response.text = "Test API joke"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        joke = self.service.get_random_joke(source='mixed')
        
        assert isinstance(joke, str)
        assert len(joke) > 0
        assert joke in self.service.local_jokes or joke == "Test API joke"