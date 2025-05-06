import time
import pytest
from prometheus_swarm.security.nonce import NonceSecurityManager

def test_nonce_generation():
    """Test nonce generation returns unique tokens."""
    nonce_manager = NonceSecurityManager()
    nonce1 = nonce_manager.generate_nonce()
    nonce2 = nonce_manager.generate_nonce()
    
    assert nonce1 != nonce2, "Generated nonces should be unique"
    assert len(nonce1) > 0, "Nonce should not be empty"

def test_nonce_validation():
    """Test nonce validation works correctly."""
    nonce_manager = NonceSecurityManager(nonce_expiration=1)
    nonce = nonce_manager.generate_nonce()
    
    # First validation should succeed
    assert nonce_manager.validate_nonce(nonce) == True
    
    # Second validation should fail (nonce already used)
    assert nonce_manager.validate_nonce(nonce) == False

def test_nonce_expiration():
    """Test nonce expiration works correctly."""
    nonce_manager = NonceSecurityManager(nonce_expiration=1)
    nonce = nonce_manager.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Validation should fail after expiration
    assert nonce_manager.validate_nonce(nonce) == False

def test_nonce_cleanup():
    """Test cleanup of expired nonces."""
    nonce_manager = NonceSecurityManager(nonce_expiration=1)
    
    # Generate multiple nonces
    nonces = [nonce_manager.generate_nonce() for _ in range(5)]
    
    # Wait for nonces to expire
    time.sleep(2)
    
    # Trigger cleanup
    nonce_manager.cleanup_expired_nonces()
    
    # Validate that no nonces remain in active nonces
    assert len(nonce_manager._active_nonces) == 0

def test_invalid_nonce():
    """Test validation of non-existent nonce."""
    nonce_manager = NonceSecurityManager()
    
    # Random nonce should not be valid
    assert nonce_manager.validate_nonce("invalid_nonce") == False