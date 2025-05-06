import pytest
import time
from unittest.mock import MagicMock, patch
from prometheus_swarm.utils.nonce_cache import NonceCache
import redis

class TestNonceCache:
    """Test suite for the NonceCache utility."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        with patch('redis.Redis') as mock:
            yield mock
    
    def test_generate_nonce(self):
        """Test nonce generation."""
        nonce_cache = NonceCache()
        
        # Generate two nonces
        nonce1 = nonce_cache.generate_nonce()
        nonce2 = nonce_cache.generate_nonce()
        
        assert nonce1 != nonce2
        assert len(nonce1) == 64  # SHA-256 hash length
    
    def test_generate_nonce_with_context(self):
        """Test nonce generation with context."""
        nonce_cache = NonceCache()
        
        # Generate nonces with different contexts
        nonce1 = nonce_cache.generate_nonce('login')
        nonce2 = nonce_cache.generate_nonce('signup')
        
        assert nonce1 != nonce2
    
    def test_store_and_check_nonce(self, mock_redis):
        """Test storing and checking nonces."""
        # Configure mock Redis
        mock_instance = mock_redis.return_value
        mock_instance.setex.return_value = True
        mock_instance.exists.return_value = True
        
        nonce_cache = NonceCache()
        
        # Store a nonce
        nonce = nonce_cache.generate_nonce()
        result = nonce_cache.store_nonce(nonce, 'test_context')
        
        # Check nonce
        is_used = nonce_cache.is_nonce_used(nonce, 'test_context')
        
        assert result is True
        assert is_used is True
    
    def test_nonce_expiration(self, mock_redis):
        """Test nonce expiration."""
        # Configure mock Redis
        mock_instance = mock_redis.return_value
        mock_instance.setex.return_value = True
        mock_instance.exists.return_value = False
        
        nonce_cache = NonceCache(nonce_expiration=1)
        
        # Store a nonce
        nonce = nonce_cache.generate_nonce()
        nonce_cache.store_nonce(nonce)
        
        # Wait for expiration
        time.sleep(2)
        
        is_used = nonce_cache.is_nonce_used(nonce)
        assert is_used is False
    
    def test_invalidate_nonce(self, mock_redis):
        """Test manual nonce invalidation."""
        # Configure mock Redis
        mock_instance = mock_redis.return_value
        mock_instance.delete.return_value = 1
        
        nonce_cache = NonceCache()
        
        # Invalidate a nonce
        nonce = nonce_cache.generate_nonce()
        deleted_count = nonce_cache.invalidate_nonce(nonce, 'test_context')
        
        assert deleted_count == 1
    
    def test_redis_error_handling(self, mock_redis):
        """Test handling of Redis connection errors."""
        # Configure mock Redis to raise exceptions
        mock_instance = mock_redis.return_value
        mock_instance.setex.side_effect = redis.exceptions.RedisError
        mock_instance.exists.side_effect = redis.exceptions.RedisError
        mock_instance.delete.side_effect = redis.exceptions.RedisError
        
        nonce_cache = NonceCache()
        
        # Test various methods with Redis errors
        nonce = nonce_cache.generate_nonce()
        
        assert nonce_cache.store_nonce(nonce) is False
        assert nonce_cache.is_nonce_used(nonce) is True
        assert nonce_cache.invalidate_nonce(nonce) == 0