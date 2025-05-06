import pytest
import time
from unittest.mock import patch, MagicMock
import redis

from prometheus_swarm.utils.nonce_cache import NonceCache

class TestNonceCache:
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client for testing."""
        with patch('redis.from_url') as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_from_url.return_value = mock_client
            yield mock_client
    
    def test_init_default(self, mock_redis):
        """Test initialization with default parameters."""
        nonce_cache = NonceCache()
        
        assert nonce_cache is not None
        mock_redis.ping.assert_called_once()
    
    def test_init_connection_error(self):
        """Test connection error handling."""
        with patch('redis.from_url') as mock_from_url:
            mock_from_url.side_effect = redis.exceptions.ConnectionError("Connection failed")
            
            with pytest.raises(ConnectionError, match="Unable to connect to Redis"):
                NonceCache()
    
    def test_generate_nonce(self, mock_redis):
        """Test nonce generation."""
        with patch('time.time') as mock_time:
            mock_time.return_value = 1234567890.0  # Fixed timestamp
            
            nonce_cache = NonceCache()
            
            # Test with different input types
            nonce1 = nonce_cache.generate_nonce("test_data")
            nonce2 = nonce_cache.generate_nonce(12345)
            
            assert len(nonce1) == 64  # SHA-256 length
            assert len(nonce2) == 64
            assert nonce1 != nonce2  # Ensure hash changes with timestamp
    
    def test_store_nonce(self, mock_redis):
        """Test storing a nonce."""
        mock_redis.set.return_value = True
        nonce_cache = NonceCache()
        
        result = nonce_cache.store_nonce("test_nonce")
        
        assert result is True
        mock_redis.set.assert_called_once_with(
            "nonce:test_nonce", 
            "1", 
            nx=True, 
            ex=3600
        )
    
    def test_is_nonce_valid(self, mock_redis):
        """Test nonce validation."""
        # First time: nonce should be valid
        mock_redis.set.return_value = True
        nonce_cache = NonceCache()
        
        valid_result = nonce_cache.is_nonce_valid("unique_nonce")
        assert valid_result is True
        
        # Second time: nonce should be invalid
        mock_redis.set.return_value = False
        invalid_result = nonce_cache.is_nonce_valid("unique_nonce")
        assert invalid_result is False
    
    def test_nonce_expiration(self, mock_redis):
        """Test custom nonce expiration."""
        custom_expiration = 60  # 1 minute
        nonce_cache = NonceCache(nonce_expiration=custom_expiration)
        
        nonce_cache.store_nonce("test_nonce")
        
        mock_redis.set.assert_called_once_with(
            "nonce:test_nonce", 
            "1", 
            nx=True, 
            ex=custom_expiration
        )
    
    def test_store_nonce_error_handling(self, mock_redis):
        """Test error handling during nonce storage."""
        mock_redis.set.side_effect = redis.exceptions.RedisError("Redis error")
        nonce_cache = NonceCache()
        
        with pytest.raises(RuntimeError, match="Error storing nonce"):
            nonce_cache.store_nonce("test_nonce")