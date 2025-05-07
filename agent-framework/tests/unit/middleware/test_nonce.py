import time
import pytest
from prometheus_swarm.middleware.nonce import NonceMiddleware

def test_nonce_generation():
    """Test that nonces are generated uniquely."""
    middleware = NonceMiddleware()
    
    # Generate multiple nonces
    nonces = set(middleware.generate_nonce() for _ in range(100))
    
    # Ensure all nonces are unique
    assert len(nonces) == 100

def test_nonce_validation():
    """Test nonce validation."""
    middleware = NonceMiddleware()
    
    # Generate a nonce
    nonce = middleware.generate_nonce()
    
    # Validate the nonce
    assert middleware.validate_nonce(nonce) == True
    
    # Attempt to validate the same nonce again (should fail)
    assert middleware.validate_nonce(nonce) == True

def test_nonce_expiration():
    """Test nonce expiration."""
    # Create middleware with very short max_age
    middleware = NonceMiddleware(max_age=1)
    
    # Generate a nonce
    nonce = middleware.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Validate expired nonce
    assert middleware.validate_nonce(nonce) == False

def test_nonce_max_limit():
    """Test that nonces are limited."""
    middleware = NonceMiddleware(max_nonces=5, max_age=10)
    
    # Generate more nonces than max_nonces
    nonces = [middleware.generate_nonce() for _ in range(10)]
    
    # Check that only max_nonces are stored (with some flexibility)
    assert len(middleware._used_nonces) <= 6
    assert len(middleware._used_nonces) >= 5

def test_nonce_uniqueness():
    """Ensure nonces are cryptographically unique."""
    middleware = NonceMiddleware()
    
    # Generate a large number of nonces
    nonces = [middleware.generate_nonce() for _ in range(1000)]
    
    # Ensure all nonces are unique
    assert len(set(nonces)) == 1000

def test_nonce_invalid_input():
    """Test validation of invalid or non-existent nonces."""
    middleware = NonceMiddleware()
    
    # Validate an arbitrary string (should fail)
    assert middleware.validate_nonce("invalid_nonce") == False