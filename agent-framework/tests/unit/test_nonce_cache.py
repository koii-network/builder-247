import pytest
import time
from prometheus_swarm.utils.nonce_cache import NonceCache

@pytest.fixture
def nonce_cache():
    """Fixture to create a NonceCache instance for testing."""
    # Use a test-specific Redis database to avoid conflicts
    return NonceCache(redis_host='localhost', redis_db=15)

def test_generate_nonce(nonce_cache):
    """Test nonce generation."""
    nonce1 = nonce_cache.generate_nonce()
    nonce2 = nonce_cache.generate_nonce()
    
    assert nonce1 != nonce2  # Ensure unique nonces
    assert len(nonce1) == 64  # SHA-256 hash is 64 characters
    assert len(nonce2) == 64

def test_validate_unique_nonce(nonce_cache):
    """Test validating a unique nonce."""
    nonce = nonce_cache.generate_nonce()
    
    # First validation should return True
    assert nonce_cache.validate_nonce(nonce) is True
    
    # Second validation should return False (replay protection)
    assert nonce_cache.validate_nonce(nonce) is False

def test_nonce_context(nonce_cache):
    """Test nonce validation with different contexts."""
    nonce = nonce_cache.generate_nonce()
    
    # Validate nonce in default context
    assert nonce_cache.validate_nonce(nonce) is True
    
    # Same nonce in a different context should be valid
    assert nonce_cache.validate_nonce(nonce, context='test_context') is True

def test_nonce_expiration(nonce_cache):
    """Test nonce expiration."""
    # Override nonce cache with very short expiry for testing
    short_expiry_cache = NonceCache(redis_host='localhost', redis_db=15, nonce_expiry=1)
    
    nonce = short_expiry_cache.generate_nonce()
    
    # Initial validation
    assert short_expiry_cache.validate_nonce(nonce) is True
    
    # Wait for expiry
    time.sleep(2)
    
    # Nonce should be valid again after expiration
    assert short_expiry_cache.validate_nonce(nonce) is True

def test_manual_nonce_clear(nonce_cache):
    """Test manual nonce clearing."""
    nonce = nonce_cache.generate_nonce()
    
    # First validation should succeed
    assert nonce_cache.validate_nonce(nonce) is True
    
    # Clear the nonce
    assert nonce_cache.clear_nonce(nonce) is True
    
    # Nonce should be valid again after clearing
    assert nonce_cache.validate_nonce(nonce) is True

def test_redis_connection_error(mocker):
    """Test error handling when Redis connection fails."""
    # Mock Redis client to simulate connection failure
    mock_redis = mocker.Mock()
    mock_redis.setex.side_effect = Exception("Redis connection error")
    
    nonce_cache = NonceCache()
    nonce_cache.redis_client = mock_redis
    
    nonce = nonce_cache.generate_nonce()
    
    # Method should handle connection errors gracefully
    assert nonce_cache.store_nonce(nonce) is False
    assert nonce_cache.validate_nonce(nonce) is False
    assert nonce_cache.clear_nonce(nonce) is False