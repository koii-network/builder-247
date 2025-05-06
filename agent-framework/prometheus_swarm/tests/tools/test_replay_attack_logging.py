"""
Test suite for Replay Attack Logging Service.
"""

import time
import pytest
from prometheus_swarm.tools.replay_attack_logging.service import ReplayAttackLogger

def test_unique_request_logging():
    """Test logging of unique requests."""
    logger = ReplayAttackLogger(expiration_minutes=1)
    
    request1 = {"user_id": 1, "action": "login"}
    request2 = {"user_id": 2, "action": "login"}
    
    assert logger.log_request(request1) is True
    assert logger.log_request(request2) is True

def test_replay_attack_detection():
    """Test detection of replay attacks with identical requests."""
    logger = ReplayAttackLogger(expiration_minutes=1)
    
    request = {"user_id": 1, "action": "transfer", "amount": 100}
    
    assert logger.log_request(request) is True
    assert logger.log_request(request) is False

def test_request_expiration():
    """Test that request signatures expire after specified time."""
    logger = ReplayAttackLogger(expiration_minutes=1)
    
    request = {"user_id": 1, "action": "login"}
    
    assert logger.log_request(request) is True
    
    # Simulate time passing
    time.sleep(61)  # Just over 1 minute
    
    assert logger.log_request(request) is True

def test_cache_size_management():
    """Test that the logger manages cache size effectively."""
    logger = ReplayAttackLogger(expiration_minutes=1)
    
    # Log multiple unique requests
    for i in range(100):
        request = {"user_id": i, "action": "login"}
        assert logger.log_request(request) is True

def test_thread_safety():
    """Basic test to ensure thread-safe operations."""
    from concurrent.futures import ThreadPoolExecutor
    
    logger = ReplayAttackLogger(expiration_minutes=1)
    request = {"user_id": 1, "action": "login"}
    
    def worker(_):
        return logger.log_request(request)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(worker, range(10)))
    
    # Only the first request should return True
    assert results.count(True) == 1
    assert results.count(False) == 9

def test_cache_clearing():
    """Test manual cache clearing functionality."""
    logger = ReplayAttackLogger(expiration_minutes=1)
    
    request = {"user_id": 1, "action": "login"}
    
    assert logger.log_request(request) is True
    
    logger.clear_cache()
    
    assert logger.log_request(request) is True