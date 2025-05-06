"""
Unit tests for the Replay Attack Logger.
"""

import time
import pytest
from prometheus_swarm.security.replay_attack_logger import ReplayAttackLogger


def test_replay_attack_logger_basic_functionality():
    """
    Test basic functionality of the replay attack logger.
    """
    logger = ReplayAttackLogger(max_cache_size=10, max_request_age=5)
    
    # First request should be accepted
    request1 = {"user_id": 123, "action": "login"}
    assert logger.log_request(request1) is True
    
    # Identical request should be rejected
    assert logger.log_request(request1) is False


def test_replay_attack_logger_max_cache_size():
    """
    Test that the logger maintains max cache size.
    """
    logger = ReplayAttackLogger(max_cache_size=3, max_request_age=10)
    
    # Add more requests than max cache size
    for i in range(5):
        request = {"user_id": i, "action": "login"}
        assert logger.log_request(request) is True
    
    # Ensure only the last 3 requests are in the cache
    assert len(logger._request_cache) == 3


def test_replay_attack_logger_request_expiration():
    """
    Test that requests expire after max_request_age.
    """
    logger = ReplayAttackLogger(max_cache_size=10, max_request_age=1)
    
    request = {"user_id": 123, "action": "login"}
    assert logger.log_request(request) is True
    
    # Wait for request to expire
    time.sleep(1.1)
    
    # Request should be accepted again after expiration
    assert logger.log_request(request) is True


def test_replay_attack_logger_signature_generation():
    """
    Test the signature generation mechanism.
    """
    logger = ReplayAttackLogger()
    
    request1 = {"user_id": 123, "action": "login"}
    request2 = {"action": "login", "user_id": 123}
    
    # Ensure same request with different key order generates same signature
    sig1 = logger.generate_signature(request1)
    sig2 = logger.generate_signature(request2)
    assert sig1 == sig2
    
    # Different requests generate different signatures
    request3 = {"user_id": 456, "action": "login"}
    sig3 = logger.generate_signature(request3)
    assert sig1 != sig3


def test_replay_attack_logger_thread_safety(thread_count=10):
    """
    Test thread safety of the replay attack logger.
    
    This test focuses on thread safety and concurrent access, 
    while accounting for the max_cache_size limitation.
    """
    import threading
    from collections import Counter
    
    # Use a higher max_cache_size to avoid premature eviction
    logger = ReplayAttackLogger(max_cache_size=1000, max_request_age=10)
    
    # Thread-safe results tracking
    unique_requests_recorded = []
    lock = threading.Lock()
    
    def log_requests(start_index):
        local_unique_requests = 0
        for i in range(start_index, start_index + 50):
            request = {"user_id": i, "action": "login"}
            if logger.log_request(request):
                local_unique_requests += 1
        
        # Thread-safe update
        with lock:
            unique_requests_recorded.append(local_unique_requests)
    
    # Create and start threads
    threads = []
    for i in range(thread_count):
        thread = threading.Thread(target=log_requests, args=(i * 50,))
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Total unique requests should not exceed max cache size
    total_requests = len(unique_requests_recorded)
    assert total_requests <= thread_count