import pytest
import time
from src.replay_attack_logger import ReplayAttackLogger


def test_basic_replay_attack_prevention():
    """Test basic replay attack prevention."""
    logger = ReplayAttackLogger(ttl=5.0)
    
    request1 = {"user_id": "123", "action": "login"}
    request2 = {"user_id": "123", "action": "login"}
    
    # First time should allow
    assert logger.check_and_log(request1) is True
    
    # Second time should block (same request)
    assert logger.check_and_log(request1) is False
    
    # Similar but not exact request should be allowed
    request2 = {"user_id": "123", "action": "logout"}
    assert logger.check_and_log(request2) is True


def test_entry_count_limit():
    """Test that max entries are enforced."""
    logger = ReplayAttackLogger(max_entries=2, ttl=5.0)
    
    request1 = {"user_id": "1", "action": "test"}
    request2 = {"user_id": "2", "action": "test"}
    request3 = {"user_id": "3", "action": "test"}
    
    assert logger.check_and_log(request1) is True
    assert logger.check_and_log(request2) is True
    assert logger.get_entry_count() == 2
    
    # This should remove the oldest entry
    assert logger.check_and_log(request3) is True
    assert logger.get_entry_count() == 2


def test_time_to_live():
    """Test that entries expire after TTL."""
    logger = ReplayAttackLogger(ttl=0.1)  # Very short TTL
    
    request = {"user_id": "123", "action": "login"}
    
    assert logger.check_and_log(request) is True
    
    # Wait for TTL to expire
    time.sleep(0.2)
    
    # Should allow again after TTL
    assert logger.check_and_log(request) is True


def test_thread_safety():
    """Basic thread safety test."""
    from threading import Thread
    
    logger = ReplayAttackLogger()
    request = {"user_id": "123", "action": "login"}
    
    def worker():
        for _ in range(100):
            logger.check_and_log(request)
    
    threads = [Thread(target=worker) for _ in range(10)]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    # There should only be one entry
    assert logger.get_entry_count() == 1


def test_different_dict_order():
    """Ensure hash is consistent regardless of dict order."""
    logger = ReplayAttackLogger()
    
    request1 = {"a": 1, "b": 2}
    request2 = {"b": 2, "a": 1}
    
    assert logger.check_and_log(request1) is True
    assert logger.check_and_log(request2) is False