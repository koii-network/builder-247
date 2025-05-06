"""Tests for NonceManager."""

import time
import pytest
from prometheus_swarm.utils.nonce_manager import NonceManager, NonceError


def test_generate_nonce():
    """Test nonce generation."""
    manager = NonceManager()
    nonce = manager.generate_nonce()
    
    assert nonce is not None
    assert ":" in nonce  # Check nonce has timestamp
    assert len(manager._nonces) == 1  # Nonce is tracked


def test_generate_nonce_with_context():
    """Test nonce generation with specific context."""
    manager = NonceManager()
    context = "test_operation"
    nonce = manager.generate_nonce(context)
    
    assert nonce is not None
    assert manager._nonces[nonce]['context'] == context


def test_validate_valid_nonce():
    """Test successful nonce validation."""
    manager = NonceManager(max_age=3600, max_uses=1)
    nonce = manager.generate_nonce()
    
    assert manager.validate_nonce(nonce) is True
    assert manager._nonces[nonce]['uses'] == 1


def test_validate_nonce_with_context():
    """Test nonce validation with context."""
    manager = NonceManager()
    context = "specific_operation"
    nonce = manager.generate_nonce(context)
    
    assert manager.validate_nonce(nonce, context) is True


def test_validate_nonce_context_mismatch():
    """Test nonce validation fails with context mismatch."""
    manager = NonceManager()
    nonce = manager.generate_nonce("original_context")
    
    with pytest.raises(NonceError, match="Context mismatch"):
        manager.validate_nonce(nonce, "different_context")


def test_validate_expired_nonce():
    """Test nonce validation fails after expiration."""
    class SlowNonceManager(NonceManager):
        def generate_nonce(self, context=None):
            nonce = super().generate_nonce(context)
            # Artificially set creation time to past
            self._nonces[nonce]['created_at'] -= 3601  # More than 1 hour ago
            return nonce

    manager = SlowNonceManager(max_age=3600)
    nonce = manager.generate_nonce()
    
    with pytest.raises(NonceError, match="Expired"):
        manager.validate_nonce(nonce)


def test_validate_overused_nonce():
    """Test nonce validation fails after maximum uses."""
    manager = NonceManager(max_uses=1)
    nonce = manager.generate_nonce()
    
    assert manager.validate_nonce(nonce) is True
    
    with pytest.raises(NonceError, match="Overused"):
        manager.validate_nonce(nonce)


def test_remove_nonce():
    """Test manual nonce removal."""
    manager = NonceManager()
    nonce = manager.generate_nonce()
    
    assert len(manager._nonces) == 1
    
    manager.remove_nonce(nonce)
    assert len(manager._nonces) == 0


def test_cleanup_expired_nonces():
    """Test cleanup of expired nonces."""
    class FastExpirationNonceManager(NonceManager):
        def generate_nonce(self, context=None):
            nonce = super().generate_nonce(context)
            # Artificially set creation time to past
            self._nonces[nonce]['created_at'] -= 3601  # More than 1 hour ago
            return nonce

    manager = FastExpirationNonceManager(max_age=3600)
    
    # Generate multiple nonces
    nonces = [manager.generate_nonce(f"context_{i}") for i in range(5)]
    
    removed_count = manager.cleanup_expired_nonces()
    assert removed_count == 5
    assert len(manager._nonces) == 0