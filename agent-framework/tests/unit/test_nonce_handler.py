"""Tests for NonceManager nonce handling and error management."""

import time
import pytest
from prometheus_swarm.utils.nonce_handler import NonceManager, NonceError

def test_nonce_generation():
    """Test basic nonce generation."""
    nonce_manager = NonceManager()
    nonce = nonce_manager.generate_nonce()
    assert isinstance(nonce, str)
    assert len(nonce) > 0

def test_nonce_validation():
    """Test successful nonce validation."""
    nonce_manager = NonceManager()
    nonce = nonce_manager.generate_nonce(context="test")
    assert nonce_manager.validate_nonce(nonce, context="test") is True

def test_nonce_context_validation():
    """Test context validation during nonce generation and consumption."""
    nonce_manager = NonceManager()
    nonce = nonce_manager.generate_nonce(context="specific_operation")
    
    # Correct context passes
    assert nonce_manager.validate_nonce(nonce, context="specific_operation") is True
    
    # Incorrect context raises an error
    with pytest.raises(NonceError, match="Nonce context invalid"):
        nonce_manager.validate_nonce(nonce, context="wrong_operation")

def test_nonce_expiration():
    """Test nonce expiration."""
    nonce_manager = NonceManager(nonce_ttl=1)  # Very short TTL
    nonce = nonce_manager.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(2)
    
    with pytest.raises(NonceError, match="Nonce has expired"):
        nonce_manager.validate_nonce(nonce)

def test_nonce_reuse_prevention():
    """Test prevention of nonce reuse."""
    nonce_manager = NonceManager()
    nonce = nonce_manager.generate_nonce()
    
    # First validation succeeds
    assert nonce_manager.validate_nonce(nonce) is True
    
    # Second validation fails
    with pytest.raises(NonceError, match="Nonce has already been consumed"):
        nonce_manager.validate_nonce(nonce)

def test_cleanup_expired_nonces():
    """Test cleanup of expired nonces."""
    nonce_manager = NonceManager(nonce_ttl=1)
    nonces = [nonce_manager.generate_nonce() for _ in range(5)]
    
    time.sleep(2)  # Wait for nonces to expire
    
    removed_count = nonce_manager.cleanup_expired_nonces()
    assert removed_count > 0

def test_unique_nonce_generation():
    """Test generation of unique nonces."""
    nonce_manager = NonceManager()
    nonce_set = set()
    
    for _ in range(100):  # Generate many nonces
        nonce = nonce_manager.generate_nonce()
        assert nonce not in nonce_set
        nonce_set.add(nonce)

def test_nonce_with_secret_key():
    """Test nonce generation with secret key."""
    nonce_manager = NonceManager()
    secret_key = "my_super_secret_key"
    
    nonce1 = nonce_manager.generate_nonce(secret_key=secret_key)
    nonce2 = nonce_manager.generate_nonce(secret_key=secret_key)
    
    assert nonce1 != nonce2  # Should generate different nonces