import time
import pytest
from prometheus_swarm.security.replay_attack_logger import ReplayAttackLogger

def test_unique_request_logging():
    """Test that unique requests are logged successfully."""
    logger = ReplayAttackLogger()
    
    # First request should be unique
    assert logger.log_and_validate("unique_request_1") == True
    
    # Duplicate request should be rejected
    assert logger.log_and_validate("unique_request_1") == False

def test_different_requests_logging():
    """Test that different requests are logged independently."""
    logger = ReplayAttackLogger()
    
    assert logger.log_and_validate("request_1") == True
    assert logger.log_and_validate("request_2") == True

def test_replay_attack_prevention_timeout():
    """Test that requests become valid again after TTL expires."""
    logger = ReplayAttackLogger(ttl=1)  # Set very short TTL
    
    # First request
    assert logger.log_and_validate("replay_test") == True
    
    # Immediate duplicate should be rejected
    assert logger.log_and_validate("replay_test") == False
    
    # Wait for TTL to expire
    time.sleep(1.1)
    
    # Request should now be valid again
    assert logger.log_and_validate("replay_test") == True

def test_max_entries_limit():
    """Test that logger enforces maximum entries limit and removes oldest entries."""
    logger = ReplayAttackLogger(max_entries=3, ttl=10)
    
    # Log more than max_entries
    assert logger.log_and_validate("req1") == True
    assert logger.log_and_validate("req2") == True
    assert logger.log_and_validate("req3") == True
    assert logger.log_and_validate("req4") == True
    
    # The first request (req1) should still be unique because it was the first that was dropped
    assert logger.log_and_validate("req1") == True
    
    # But if tried again immediately, it should be rejected
    assert logger.log_and_validate("req1") == False

def test_thread_safety():
    """Basic test to ensure thread safety."""
    from concurrent.futures import ThreadPoolExecutor
    
    logger = ReplayAttackLogger()
    
    def log_request(req):
        return logger.log_and_validate(req)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(log_request, ["req1"] * 10))
    
    # Only first thread should return True
    assert results.count(True) == 1
    assert results.count(False) == 9

def test_clear_logs():
    """Test clearing all logs."""
    logger = ReplayAttackLogger()
    
    assert logger.log_and_validate("req1") == True
    assert logger.log_and_validate("req1") == False
    
    logger.clear_logs()
    
    # After clearing, request should be unique again
    assert logger.log_and_validate("req1") == True