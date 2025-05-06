import time
import pytest
from prometheus_swarm.security.replay_attack_logger import ReplayAttackLogger

def test_basic_replay_detection():
    """Test basic replay attack detection."""
    logger = ReplayAttackLogger(max_cache_size=100, expiration_time=300)
    request_data = {"user_id": 123, "action": "login"}
    
    # First request should return False
    assert logger.is_replay(request_data) is False
    
    # Same request should now be detected as a replay
    assert logger.is_replay(request_data) is True

def test_different_requests():
    """Verify that different requests are not flagged as replays."""
    logger = ReplayAttackLogger(max_cache_size=100, expiration_time=300)
    request1 = {"user_id": 123, "action": "login"}
    request2 = {"user_id": 456, "action": "login"}
    
    assert logger.is_replay(request1) is False
    assert logger.is_replay(request2) is False

def test_request_expiration():
    """Test that requests expire after the specified time."""
    logger = ReplayAttackLogger(max_cache_size=100, expiration_time=1)
    request_data = {"user_id": 123, "action": "login"}
    
    assert logger.is_replay(request_data) is False
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Request should no longer be considered a replay
    assert logger.is_replay(request_data) is False

def test_max_cache_size():
    """Verify that the cache respects the maximum size."""
    logger = ReplayAttackLogger(max_cache_size=3, expiration_time=300)
    
    # Add 4 unique requests
    request1 = {"user_id": 1, "action": "login"}
    request2 = {"user_id": 2, "action": "login"}
    request3 = {"user_id": 3, "action": "login"}
    request4 = {"user_id": 4, "action": "login"}
    
    logger.is_replay(request1)
    logger.is_replay(request2)
    logger.is_replay(request3)
    logger.is_replay(request4)
    
    # Cache size should be limited to max_cache_size
    assert logger.get_cache_size() == 3

def test_signature_uniqueness():
    """Ensure that requests with the same content are considered replays."""
    logger = ReplayAttackLogger(max_cache_size=100, expiration_time=300)
    
    request1 = {"user_id": 123, "data": "sensitive"}
    request2 = {"data": "sensitive", "user_id": 123}  # Same data, different order
    
    assert logger.is_replay(request1) is False
    assert logger.is_replay(request2) is False  # Because order doesn't matter

def test_invalid_input():
    """Test handling of various input types."""
    logger = ReplayAttackLogger()
    
    # Various request data types
    inputs = [
        {"key": "value"},
        {"nested": {"inner": "data"}},
        {"list": [1, 2, 3]},
    ]
    
    for input_data in inputs:
        assert logger.is_replay(input_data) is False
        assert logger.is_replay(input_data) is True  # Replay detection