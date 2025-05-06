import pytest
import time
from datetime import datetime, timedelta
from prometheus_swarm.database.nonce import NonceManager

def test_nonce_generation():
    """Test nonce generation produces unique tokens."""
    nonce_manager = NonceManager()
    
    # Generate multiple nonces and ensure they are unique
    nonce1 = nonce_manager.generate_nonce()
    nonce2 = nonce_manager.generate_nonce()
    
    assert nonce1 != nonce2
    assert len(nonce1) == 64  # SHA-256 hash length
    assert len(nonce2) == 64

def test_nonce_validation():
    """Test basic nonce validation."""
    nonce_manager = NonceManager()
    
    nonce = nonce_manager.generate_nonce()
    
    # First validation should succeed
    assert nonce_manager.validate_nonce(nonce) is True
    
    # Second validation should fail (nonce already used)
    assert nonce_manager.validate_nonce(nonce) is False

def test_nonce_context():
    """Test nonce validation with context."""
    nonce_manager = NonceManager()
    
    nonce1 = nonce_manager.generate_nonce(context='login')
    nonce2 = nonce_manager.generate_nonce(context='signup')
    
    # Validate with correct context
    assert nonce_manager.validate_nonce(nonce1, context='login') is True
    assert nonce_manager.validate_nonce(nonce2, context='signup') is True
    
    # Validate with incorrect context
    assert nonce_manager.validate_nonce(nonce1, context='signup') is False
    assert nonce_manager.validate_nonce(nonce2, context='login') is False

def test_nonce_expiration():
    """Test nonce expiration."""
    # Create a very short-lived nonce manager
    nonce_manager = NonceManager(max_age=1)
    
    nonce = nonce_manager.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Validation should fail after expiration
    assert nonce_manager.validate_nonce(nonce) is False

def test_clear_expired_nonces():
    """Test clearing expired nonces."""
    nonce_manager = NonceManager(max_age=1)
    
    # Generate multiple nonces
    nonce1 = nonce_manager.generate_nonce()
    nonce2 = nonce_manager.generate_nonce()
    
    # Wait for nonces to expire
    time.sleep(2)
    
    # Clear expired nonces
    expired_count = nonce_manager.clear_expired_nonces()
    
    assert expired_count == 2
    assert nonce_manager.validate_nonce(nonce1) is False
    assert nonce_manager.validate_nonce(nonce2) is False

def test_invalid_nonce():
    """Test validation of non-existent nonce."""
    nonce_manager = NonceManager()
    
    # Validate a nonce that was never generated
    assert nonce_manager.validate_nonce('invalid_nonce') is False