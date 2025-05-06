import time
import pytest
from prometheus_swarm.utils.replay_prevention import ReplayAttackPrevention

def test_replay_attack_prevention_basic():
    """Test basic replay attack prevention functionality."""
    rap = ReplayAttackPrevention(max_time_diff=10, max_nonce_cache=3)
    
    # First request with a nonce should be valid
    assert rap.is_request_valid(time.time(), "nonce1") == True
    
    # Same nonce should be rejected
    assert rap.is_request_valid(time.time(), "nonce1") == False

def test_replay_attack_prevention_timestamp():
    """Test timestamp validation."""
    rap = ReplayAttackPrevention(max_time_diff=1)
    
    # Request with current timestamp should be valid
    assert rap.is_request_valid(time.time(), "nonce2") == True
    
    # Request with outdated timestamp should be invalid
    with pytest.raises(Exception):
        rap.is_request_valid(time.time() - 100, "nonce3")

def test_nonce_cache_size():
    """Test that nonce cache does not exceed max size."""
    rap = ReplayAttackPrevention(max_time_diff=10, max_nonce_cache=3)
    
    # Add 4 unique nonces (exceeding cache size)
    assert rap.is_request_valid(time.time(), "nonce1") == True
    assert rap.is_request_valid(time.time(), "nonce2") == True
    assert rap.is_request_valid(time.time(), "nonce3") == True
    assert rap.is_request_valid(time.time(), "nonce4") == True
    
    # The first nonce should have been removed
    assert len(rap.is_request_valid) == 3

def test_decorator():
    """Test decorator functionality."""
    rap = ReplayAttackPrevention()
    
    @rap.decorator
    def example_function(timestamp=None, nonce=None):
        return True
    
    # Valid request
    assert example_function(timestamp=time.time(), nonce="test_nonce") == True
    
    # Replay attack (same nonce)
    with pytest.raises(ValueError):
        example_function(timestamp=time.time(), nonce="test_nonce")
    
    # Missing nonce
    with pytest.raises(ValueError):
        example_function(timestamp=time.time())