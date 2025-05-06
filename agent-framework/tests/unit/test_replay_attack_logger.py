import time
import threading
import pytest
from prometheus_swarm.utils.replay_attack_logger import ReplayAttackLogger

def test_replay_attack_logger_basic_functionality():
    """Test basic replay attack logging functionality."""
    logger = ReplayAttackLogger(expiration_time=1)
    
    # First request should be allowed
    assert logger.log_request("request1") is True
    
    # Same request should be blocked
    assert logger.log_request("request1") is False
    
    # Different request should be allowed
    assert logger.log_request("request2") is True

def test_replay_attack_logger_expiration():
    """Test that requests expire after specified time."""
    logger = ReplayAttackLogger(expiration_time=1)
    
    # Log a request
    assert logger.log_request("request1") is True
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Request should now be allowed again
    assert logger.log_request("request1") is True

def test_replay_attack_logger_thread_safety():
    """Test thread safety of the replay attack logger."""
    logger = ReplayAttackLogger(expiration_time=5)
    
    def concurrent_log(request_sig):
        """Simulate concurrent request logging."""
        return logger.log_request(request_sig)
    
    # Simulate concurrent requests
    results = []
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=lambda: results.append(concurrent_log("concurrent_request")))
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Only one request should be allowed
    assert results.count(True) == 1
    assert results.count(False) == 9

def test_replay_attack_logger_clear_log():
    """Test clearing the log."""
    logger = ReplayAttackLogger()
    
    logger.log_request("request1")
    logger.log_request("request2")
    
    assert logger.get_log_size() == 2
    
    logger.clear_log()
    
    assert logger.get_log_size() == 0

def test_replay_attack_logger_max_entries():
    """Test that the logger limits the number of entries."""
    logger = ReplayAttackLogger(expiration_time=5, max_entries=3)
    
    # Log more requests than max_entries
    for i in range(5):
        logger.log_request(f"request{i}")
    
    # Check that only the most recent 3 entries remain
    assert logger.get_log_size() == 3

def test_replay_attack_logger_edge_cases():
    """Test edge cases and error handling."""
    logger = ReplayAttackLogger()
    
    # Empty signature should work
    assert logger.log_request("") is True
    
    # None signature should raise TypeError
    with pytest.raises(TypeError):
        logger.log_request(None)  # type: ignore

    # Very long signature
    long_sig = "x" * 10000
    assert logger.log_request(long_sig) is True