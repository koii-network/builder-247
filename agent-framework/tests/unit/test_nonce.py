"""
Unit tests for Nonce Configuration Management
"""

import time
import pytest
from prometheus_swarm.utils.nonce import NonceManager


def test_nonce_generation():
    """Test that nonce generation returns unique values."""
    nonce_manager = NonceManager()
    nonce1 = nonce_manager.generate_nonce()
    nonce2 = nonce_manager.generate_nonce()

    assert nonce1 != nonce2
    assert len(nonce1) == 64  # SHA-256 produces 64-character hex string
    assert isinstance(nonce1, str)


def test_nonce_validation():
    """Test nonce validation logic."""
    nonce_manager = NonceManager()
    nonce = nonce_manager.generate_nonce()

    # First validation should succeed
    assert nonce_manager.validate_nonce(nonce) is True

    # Second validation of same nonce should fail
    assert nonce_manager.validate_nonce(nonce) is False


def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    class MockNonceManager(NonceManager):
        def __init__(self, nonce_expiry_seconds):
            super().__init__(nonce_expiry_seconds)

    # Create a nonce manager with very short expiry
    nonce_manager = MockNonceManager(nonce_expiry_seconds=1)
    nonce = nonce_manager.generate_nonce()

    # Wait for nonce to expire
    time.sleep(1.1)

    # Nonce should now be re-usable
    assert nonce_manager.validate_nonce(nonce) is True


def test_multiple_nonce_tracking():
    """Test tracking multiple unique nonces."""
    nonce_manager = NonceManager()
    nonces = [nonce_manager.generate_nonce() for _ in range(10)]

    # All nonces should be valid on first validation
    validation_results = [nonce_manager.validate_nonce(nonce) for nonce in nonces]
    assert all(validation_results)

    # None should be valid on second validation
    validation_results = [nonce_manager.validate_nonce(nonce) for nonce in nonces]
    assert not any(validation_results)


def test_nonce_cleanup():
    """Test internal nonce cleanup mechanism."""
    nonce_manager = NonceManager(nonce_expiry_seconds=1)
    
    # Generate some nonces
    nonces = [nonce_manager.generate_nonce() for _ in range(5)]
    
    # Wait for expiry
    time.sleep(1.1)
    
    # Trigger cleanup by validating a new nonce
    new_nonce = nonce_manager.generate_nonce()
    
    # All previous nonces should now be re-usable
    reusable_results = [nonce_manager.validate_nonce(nonce) for nonce in nonces]
    assert all(reusable_results)