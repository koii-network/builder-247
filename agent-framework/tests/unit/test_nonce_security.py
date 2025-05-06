import time
import pytest
from prometheus_swarm.security.nonce import NonceSecurityManager

def test_generate_nonce():
    """Test nonce generation produces unique, valid nonces."""
    nonce_manager = NonceSecurityManager()
    
    nonce1 = nonce_manager.generate_nonce()
    nonce2 = nonce_manager.generate_nonce()
    
    assert nonce1 != nonce2
    assert len(nonce1) > 0
    assert len(nonce2) > 0

def test_validate_nonce_basic():
    """Test basic nonce validation."""
    nonce_manager = NonceSecurityManager()
    
    nonce = nonce_manager.generate_nonce()
    
    assert nonce_manager.validate_nonce(nonce) is True  # First validation returns True
    assert nonce_manager.validate_nonce(nonce) is False  # Subsequent validations return False

def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    nonce_manager = NonceSecurityManager(max_age_seconds=1)
    
    nonce = nonce_manager.generate_nonce()
    time.sleep(2)  # Wait beyond max age
    
    assert nonce_manager.validate_nonce(nonce) is False  # Expired nonce should not be valid

def test_invalid_nonce():
    """Test handling of invalid/empty nonces."""
    nonce_manager = NonceSecurityManager()
    
    assert nonce_manager.validate_nonce("") is False
    assert nonce_manager.validate_nonce(None) is False

def test_cleanup_expired_nonces():
    """Test cleanup of expired nonces."""
    nonce_manager = NonceSecurityManager(max_age_seconds=1)
    
    nonce1 = nonce_manager.generate_nonce()
    nonce2 = nonce_manager.generate_nonce()
    
    time.sleep(2)  # Wait beyond max age
    
    removed_count = nonce_manager.cleanup_expired_nonces()
    assert removed_count > 0