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
    """
    prevention = ReplayAttackPrevention(window_seconds=5, max_cache_size=3)
    
    # Generate more requests than the max cache size
    request_ids = []
    for i in range(5):
        request_data = {"user": f"user{i}", "action": "test"}
        request_id = prevention.generate_request_id(request_data)
        request_ids.append(request_id)
        assert prevention.is_unique_request(request_id) is True
    
    # Check that only the last 3 requests are unique
    for request_id in request_ids[:-3]:
        assert prevention.is_unique_request(request_id) is False

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