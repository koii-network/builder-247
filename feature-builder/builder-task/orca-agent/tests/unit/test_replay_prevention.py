import time
import pytest
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.server.utils.replay_prevention import ReplayAttackPrevention

def test_replay_attack_prevention_basic():
    """Test basic replay attack prevention functionality."""
    replay_preventer = ReplayAttackPrevention(max_cache_size=10, max_request_age_seconds=5)
    
    # First request should be allowed
    request1 = {"user_id": 123, "action": "create"}
    assert not replay_preventer.is_replay_attack(request1)
    
    # Same request again should be considered a replay attack
    assert replay_preventer.is_replay_attack(request1)

def test_replay_attack_prevention_different_requests():
    """Test that different requests are treated independently."""
    replay_preventer = ReplayAttackPrevention(max_cache_size=10, max_request_age_seconds=5)
    
    request1 = {"user_id": 123, "action": "create"}
    request2 = {"user_id": 456, "action": "update"}
    
    assert not replay_preventer.is_replay_attack(request1)
    assert not replay_preventer.is_replay_attack(request2)

def test_replay_attack_prevention_cache_limit():
    """Test that the cache size limit is respected."""
    replay_preventer = ReplayAttackPrevention(max_cache_size=3, max_request_age_seconds=60)
    
    requests = [
        {"user_id": i, "action": "action"} for i in range(5)
    ]
    
    for request in requests[:3]:
        assert not replay_preventer.is_replay_attack(request)
    
    # These will cause the first request to be evicted from the cache
    for request in requests[3:]:
        assert not replay_preventer.is_replay_attack(request)
    
    # First request should now be allowed again
    assert not replay_preventer.is_replay_attack(requests[0])

def test_replay_attack_prevention_expiration():
    """Test that requests expire after a certain time."""
    replay_preventer = ReplayAttackPrevention(max_cache_size=10, max_request_age_seconds=1)
    
    request = {"user_id": 123, "action": "create"}
    
    assert not replay_preventer.is_replay_attack(request)
    
    # Simulate time passing
    time.sleep(1.1)
    
    # Request should be allowed again after expiration
    assert not replay_preventer.is_replay_attack(request)

def test_replay_attack_edge_cases():
    """Test various edge cases for replay attack prevention."""
    replay_preventer = ReplayAttackPrevention(max_cache_size=10, max_request_age_seconds=5)
    
    # Empty request
    empty_request = {}
    assert not replay_preventer.is_replay_attack(empty_request)
    assert replay_preventer.is_replay_attack(empty_request)
    
    # Request with complex nested data
    complex_request = {
        "user": {"id": 123, "role": "admin"},
        "action": "update",
        "data": [1, 2, 3]
    }
    assert not replay_preventer.is_replay_attack(complex_request)
    assert replay_preventer.is_replay_attack(complex_request)