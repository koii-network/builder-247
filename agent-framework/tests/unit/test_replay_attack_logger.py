import time
import pytest
from prometheus_swarm.utils.replay_attack_logger import ReplayAttackLogger

def test_replay_attack_logger_basic():
    """Test basic functionality of ReplayAttackLogger."""
    logger = ReplayAttackLogger(max_cache_size=10, expire_time=1)
    
    # First time request should return True
    request1 = {"user_id": 123, "action": "login"}
    assert logger.log_and_check_request(request1) is True
    
    # Same request immediately after should return False
    assert logger.log_and_check_request(request1) is False

def test_replay_attack_logger_with_time():
    """Test that requests become valid again after expiration."""
    logger = ReplayAttackLogger(max_cache_size=10, expire_time=1)
    
    request1 = {"user_id": 123, "action": "login"}
    assert logger.log_and_check_request(request1) is True
    
    # Same request immediately should be a replay attack
    assert logger.log_and_check_request(request1) is False
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Request should now be valid
    assert logger.log_and_check_request(request1) is True

def test_replay_attack_logger_max_cache_size():
    """Test that logger respects max cache size."""
    logger = ReplayAttackLogger(max_cache_size=3, expire_time=10)
    
    # Create 4 unique requests
    request1 = {"user_id": 1, "action": "login"}
    request2 = {"user_id": 2, "action": "logout"}
    request3 = {"user_id": 3, "action": "register"}
    request4 = {"user_id": 4, "action": "update"}
    
    assert logger.log_and_check_request(request1) is True
    assert logger.log_and_check_request(request2) is True
    assert logger.log_and_check_request(request3) is True
    assert logger.log_and_check_request(request4) is True  # Should push out first request
    
    # First request should now be allowed again
    assert logger.log_and_check_request(request1) is True

def test_signature_generation():
    """Test that signature generation is consistent."""
    logger = ReplayAttackLogger()
    
    request1 = {"user_id": 123, "action": "login"}
    request2 = {"action": "login", "user_id": 123}  # Same data, different order
    
    sig1 = logger.generate_signature(request1)
    sig2 = logger.generate_signature(request2)
    
    assert sig1 == sig2, "Signature generation should be order-independent"

def test_thread_safety(n_threads=10, n_iterations=100):
    """Basic thread safety test for ReplayAttackLogger."""
    import threading
    
    logger = ReplayAttackLogger(max_cache_size=1000, expire_time=10)
    request = {"user_id": 42, "action": "login"}
    
    def thread_worker():
        for _ in range(n_iterations):
            assert logger.log_and_check_request(request) is False
    
    # First thread gets the first log
    assert logger.log_and_check_request(request) is True
    
    # Create threads to attack with same request
    threads = [threading.Thread(target=thread_worker) for _ in range(n_threads)]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()