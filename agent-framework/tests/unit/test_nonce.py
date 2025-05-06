import time
import pytest
from prometheus_swarm.utils.nonce import NonceRequestInterface

def test_nonce_generation():
    """Test that nonce generation creates unique tokens."""
    nonce_interface = NonceRequestInterface()
    
    # Generate multiple nonces
    nonces = [nonce_interface.generate_nonce() for _ in range(100)]
    
    # Check that all nonces are unique
    assert len(set(nonces)) == 100

def test_nonce_validation():
    """Test nonce validation works correctly."""
    nonce_interface = NonceRequestInterface()
    
    # Generate a nonce
    nonce = nonce_interface.generate_nonce()
    
    # First validation should succeed
    assert nonce_interface.validate_nonce(nonce) is True
    
    # Second validation should fail (nonce already used)
    assert nonce_interface.validate_nonce(nonce) is False

def test_nonce_expiration():
    """Test that nonces expire after max_age."""
    # Set a very short max age for testing
    nonce_interface = NonceRequestInterface(max_age_seconds=1)
    
    # Generate a nonce
    nonce = nonce_interface.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(1.1)
    
    # Validation should now fail
    assert nonce_interface.validate_nonce(nonce) is False

def test_cleanup_expired_nonces():
    """Test cleanup of expired nonces."""
    nonce_interface = NonceRequestInterface(max_age_seconds=1)
    
    # Generate multiple nonces
    nonce1 = nonce_interface.generate_nonce()
    nonce2 = nonce_interface.generate_nonce()
    
    # Wait for nonces to expire
    time.sleep(1.1)
    
    # Cleanup expired nonces
    removed_count = nonce_interface.cleanup_expired_nonces()
    
    assert removed_count == 2

def test_nonce_with_user_id():
    """Test nonce generation with a user ID."""
    nonce_interface = NonceRequestInterface()
    
    # Generate nonces with different user IDs
    nonce1 = nonce_interface.generate_nonce(user_id='user1')
    nonce2 = nonce_interface.generate_nonce(user_id='user2')
    
    # Nonces should be different
    assert nonce1 != nonce2

def test_invalid_nonce():
    """Test validation of an invalid nonce."""
    nonce_interface = NonceRequestInterface()
    
    # Try to validate a random string
    assert nonce_interface.validate_nonce('invalid_nonce') is False