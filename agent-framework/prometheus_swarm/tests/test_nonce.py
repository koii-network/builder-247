"""
Unit tests for NonceTracker

This test suite verifies the functionality of the NonceTracker class,
ensuring robust nonce generation, validation, and tracking.
"""

import time
import pytest
from prometheus_swarm.utils.nonce import NonceTracker


def test_nonce_generation():
    """Test basic nonce generation"""
    tracker = NonceTracker()
    nonce = tracker.generate_nonce()
    assert isinstance(nonce, str)
    assert len(nonce) > 0


def test_nonce_validation():
    """Test successful nonce validation"""
    tracker = NonceTracker()
    nonce = tracker.generate_nonce()
    assert tracker.validate_nonce(nonce) is True


def test_nonce_reuse_prevention():
    """Test that a nonce can only be used once by default"""
    tracker = NonceTracker()
    nonce = tracker.generate_nonce()
    
    # First validation should succeed
    assert tracker.validate_nonce(nonce) is True
    
    # Second validation should fail
    assert tracker.validate_nonce(nonce) is False


def test_nonce_namespace_isolation():
    """Test that nonces are isolated across namespaces"""
    tracker = NonceTracker()
    
    nonce1 = tracker.generate_nonce('namespace1')
    nonce2 = tracker.generate_nonce('namespace2')
    
    assert tracker.validate_nonce(nonce1, 'namespace1') is True
    assert tracker.validate_nonce(nonce2, 'namespace2') is True
    
    # Cross-namespace validation should fail
    assert tracker.validate_nonce(nonce1, 'namespace2') is False
    assert tracker.validate_nonce(nonce2, 'namespace1') is False


def test_nonce_expiration():
    """Test nonce expiration mechanism"""
    tracker = NonceTracker(max_age=1)  # 1-second expiration
    
    nonce = tracker.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Validate should now fail
    assert tracker.validate_nonce(nonce) is False


def test_invalid_nonce():
    """Test validation of an invalid/non-existent nonce"""
    tracker = NonceTracker()
    
    assert tracker.validate_nonce('invalid_nonce') is False


def test_optional_reuse():
    """Test nonce validation with reuse allowed"""
    tracker = NonceTracker()
    nonce = tracker.generate_nonce()
    
    # Validate multiple times when reuse is allowed
    assert tracker.validate_nonce(nonce, use_once=False) is True
    assert tracker.validate_nonce(nonce, use_once=False) is True