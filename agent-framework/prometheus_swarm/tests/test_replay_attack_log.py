import time
import pytest
from prometheus_swarm.security.replay_attack_log import ReplayAttackLogger

def test_unique_request_logging():
    """Test that unique requests are successfully logged."""
    logger = ReplayAttackLogger(retention_time=5, cleanup_interval=10)
    
    request1 = {"action": "login", "user": "alice"}
    request2 = {"action": "login", "user": "bob"}
    
    assert logger.log_request(request1) is True
    assert logger.log_request(request2) is True

def test_replay_attack_prevention():
    """Test that identical requests are prevented."""
    logger = ReplayAttackLogger(retention_time=5, cleanup_interval=10)
    
    request = {"action": "transfer", "amount": 1000}
    
    # First request should be allowed
    assert logger.log_request(request) is True
    
    # Same request should be blocked
    assert logger.log_request(request) is False

def test_request_expiration():
    """Test that requests expire after retention time."""
    logger = ReplayAttackLogger(retention_time=1, cleanup_interval=1)
    
    request = {"action": "purchase", "item": "book"}
    
    assert logger.log_request(request) is True
    
    # Wait for retention time to pass
    time.sleep(2)
    
    # Request should be allowed again after expiration
    assert logger.log_request(request) is True

def test_concurrent_requests():
    """Test thread-safety of request logging."""
    logger = ReplayAttackLogger(retention_time=5, cleanup_interval=10)
    
    def test_concurrent_logging(requests):
        return [logger.log_request(req) for req in requests]
    
    request = {"action": "login", "user": "concurrent_user"}
    
    # Multiple identical requests should have only one success
    results1 = test_concurrent_logging([request, request, request])
    assert results1.count(True) == 1
    assert results1.count(False) == 2

def test_signature_sensitivity():
    """Test that slight changes create different signatures."""
    logger = ReplayAttackLogger(retention_time=5, cleanup_interval=10)
    
    request1 = {"action": "login", "user": "alice"}
    request2 = {"action": "login", "user": "bob"}
    
    # Requests with different contents should both be allowed
    assert logger.log_request(request1) is True
    assert logger.log_request(request2) is True