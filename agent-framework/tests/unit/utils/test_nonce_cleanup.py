import time
import pytest
from prometheus_swarm.utils.nonce_cleanup import NonceCleanup

def test_nonce_cleanup_initialization():
    """Test the initialization of NonceCleanup."""
    nonce_manager = NonceCleanup()
    assert nonce_manager is not None

def test_add_and_check_nonce():
    """Test adding and checking nonces."""
    nonce_manager = NonceCleanup()
    
    # Add a new nonce
    result = nonce_manager.add_nonce("test_nonce")
    assert result is True
    
    # Try to add the same nonce again
    result = nonce_manager.add_nonce("test_nonce")
    assert result is False
    
    # Check if nonce is used
    assert nonce_manager.is_nonce_used("test_nonce") is True

def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    # Create a nonce manager with very short expiration time
    nonce_manager = NonceCleanup(expiration_time_seconds=1)
    
    nonce_manager.add_nonce("expired_nonce")
    
    # Wait for expiration
    time.sleep(1.5)
    
    # Cleanup expired nonces
    expired = nonce_manager.cleanup_expired_nonces()
    assert "expired_nonce" in expired
    assert nonce_manager.is_nonce_used("expired_nonce") is False

def test_nonce_age():
    """Test getting nonce age."""
    nonce_manager = NonceCleanup()
    
    nonce_manager.add_nonce("age_test_nonce")
    
    # Check nonce age
    age = nonce_manager.get_nonce_age("age_test_nonce")
    assert age is not None
    assert age >= 0
    
    # Check non-existent nonce
    assert nonce_manager.get_nonce_age("non_existent_nonce") is None

def test_nonce_reset():
    """Test resetting the nonce manager."""
    nonce_manager = NonceCleanup()
    
    nonce_manager.add_nonce("reset_nonce1")
    nonce_manager.add_nonce("reset_nonce2")
    
    nonce_manager.reset()
    
    assert nonce_manager.is_nonce_used("reset_nonce1") is False
    assert nonce_manager.is_nonce_used("reset_nonce2") is False