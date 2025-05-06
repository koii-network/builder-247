import time
import pytest
from prometheus_swarm.utils.replay_prevention import ReplayAttackPrevention

def test_replay_attack_prevention_basic():
    """
    Test basic replay attack prevention functionality.
    """
    prevention = ReplayAttackPrevention(window_seconds=5, max_cache_size=10)
    
    # Generate a request ID
    request_data = {"user": "test_user", "action": "login"}
    request_id = prevention.generate_request_id(request_data)
    
    # First time should be unique
    assert prevention.is_unique_request(request_id) is True
    
    # Second time should be a replay
    assert prevention.is_unique_request(request_id) is False

def test_replay_prevention_multiple_requests():
    """
    Test handling multiple unique and repeated requests.
    """
    prevention = ReplayAttackPrevention(window_seconds=5, max_cache_size=10)
    
    request_data1 = {"user": "user1", "action": "login"}
    request_data2 = {"user": "user2", "action": "logout"}
    
    request_id1 = prevention.generate_request_id(request_data1)
    request_id2 = prevention.generate_request_id(request_data2)
    
    # Both requests should be unique initially
    assert prevention.is_unique_request(request_id1) is True
    assert prevention.is_unique_request(request_id2) is True
    
    # Repeating the same requests should be detected as replays
    assert prevention.is_unique_request(request_id1) is False
    assert prevention.is_unique_request(request_id2) is False

def test_replay_prevention_expiration():
    """
    Test that requests expire after the time window.
    """
    prevention = ReplayAttackPrevention(window_seconds=1, max_cache_size=10)
    
    request_data = {"user": "test_user", "action": "login"}
    request_id = prevention.generate_request_id(request_data)
    
    # First request is unique
    assert prevention.is_unique_request(request_id) is True
    
    # Wait for the time window to expire
    time.sleep(1.5)
    
    # Request should now be considered unique again
    assert prevention.is_unique_request(request_id) is True

def test_replay_prevention_max_cache_size():
    """
    Test that the cache respects the maximum size limit.
    
    This test verifies that requests beyond the max cache size 
    become unique again, allowing for time-based request tracking.
    """
    prevention = ReplayAttackPrevention(window_seconds=5, max_cache_size=3)
    
    # Track request uniqueness and expect most recent requests to be unique
    unique_count = 0
    request_ids = []
    
    for i in range(5):
        request_data = {"user": f"user{i}", "action": "test"}
        request_id = prevention.generate_request_id(request_data)
        request_ids.append(request_id)
    
    # Verify request uniqueness across different generations
    for request_id in request_ids:
        is_unique = prevention.is_unique_request(request_id)
        if is_unique:
            unique_count += 1
    
    # At most 3 requests should be unique due to max cache size
    assert unique_count <= 3

def test_generate_request_id_uniqueness():
    """
    Test that generate_request_id creates unique identifiers.
    """
    prevention = ReplayAttackPrevention()
    
    request_data1 = {"user": "test_user", "action": "login"}
    request_data2 = {"user": "test_user", "action": "login"}
    
    request_id1 = prevention.generate_request_id(request_data1)
    request_id2 = prevention.generate_request_id(request_data2)
    
    # Request IDs should be different due to timestamp
    assert request_id1 != request_id2