"""
Test suite for Replay Attack Alert Mechanism
"""

import time
import pytest
from prometheus_swarm.security.replay_attack_alert import (
    ReplayAttackPreventor, 
    prevent_replay_attack
)

def test_replay_attack_preventor_basic():
    """Test basic functionality of ReplayAttackPreventor"""
    preventor = ReplayAttackPreventor(cache_expiry_seconds=1)
    
    # First request should be allowed
    assert not preventor.is_replay_attempt("signature1")
    
    # Same signature should now be considered a replay attempt
    assert preventor.is_replay_attempt("signature1")

def test_replay_attack_preventor_expiry():
    """Test request signature expiration"""
    preventor = ReplayAttackPreventor(cache_expiry_seconds=1)
    
    preventor.is_replay_attempt("signature1")
    time.sleep(1.1)  # Wait for expiry
    
    # After expiry, the same signature should be allowed again
    assert not preventor.is_replay_attempt("signature1")

def test_decorator_basic():
    """Test basic decorator functionality"""
    call_count = 0
    
    @prevent_replay_attack()
    def example_function(param):
        nonlocal call_count
        call_count += 1
        return param
    
    # First call succeeds
    result1 = example_function("test")
    assert result1 == "test"
    assert call_count == 1
    
    # Second call (with same params) returns None
    result2 = example_function("test")
    assert result2 is None
    assert call_count == 1

def test_decorator_with_custom_signature():
    """Test decorator with custom signature generation"""
    call_count = 0
    
    def custom_signature(x, y):
        return f"{x}_{y}"
    
    @prevent_replay_attack(request_signature_func=custom_signature)
    def example_function(x, y):
        nonlocal call_count
        call_count += 1
        return x + y
    
    # First call succeeds
    result1 = example_function(1, 2)
    assert result1 == 3
    assert call_count == 1
    
    # Same parameters trigger replay prevention
    result2 = example_function(1, 2)
    assert result2 is None
    assert call_count == 1

def test_decorator_raise_on_replay():
    """Test decorator's ability to raise on replay attempt"""
    @prevent_replay_attack(raise_on_replay=True)
    def example_function(param):
        return param
    
    # First call succeeds
    result1 = example_function("test")
    assert result1 == "test"
    
    # Second call raises an exception
    with pytest.raises(ValueError, match="Potential replay attack detected"):
        example_function("test")