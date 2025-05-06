import time
import pytest
from prometheus_swarm.utils.replay_attack_logging import ReplayAttackLogger

def test_generate_unique_signatures():
    """
    Test that each request generates a unique signature.
    """
    logger = ReplayAttackLogger()
    
    # Simple request data
    request1 = {"user_id": 123, "action": "login"}
    request2 = {"user_id": 123, "action": "login"}
    
    sig1 = logger.log_request(request1)
    time.sleep(0.1)  # Slight delay to ensure different timestamps
    sig2 = logger.log_request(request2)
    
    assert sig1 != sig2, "Signatures should be unique even for identical requests"

def test_replay_attack_prevention():
    """
    Test that logging the same request within expiration time raises an exception.
    """
    logger = ReplayAttackLogger(expiration_time=1)
    
    request = {"user_id": 456, "action": "purchase"}
    
    # First log should succeed
    signature = logger.log_request(request)
    
    # Immediate replay should fail
    with pytest.raises(ValueError, match="Potential replay attack detected"):
        logger.log_request(request)

def test_cache_size_limit():
    """
    Test that the cache does not exceed the specified size.
    """
    logger = ReplayAttackLogger(cache_size=3)
    
    # Log 5 different requests
    requests = [
        {"id": 1},
        {"id": 2},
        {"id": 3},
        {"id": 4},
        {"id": 5}
    ]
    
    signatures = []
    for req in requests:
        signatures.append(logger.log_request(req))
    
    # First two signatures should be out of cache
    assert len(logger._cache) == 3
    assert all(sig in logger._cache for sig in signatures[-3:])

def test_signature_expiration():
    """
    Test that signatures expire after the specified time.
    """
    logger = ReplayAttackLogger(expiration_time=1)
    
    request = {"user_id": 789, "action": "transfer"}
    
    # Log request
    signature = logger.log_request(request)
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Should now be able to log the same request again
    new_signature = logger.log_request(request)
    assert new_signature != signature

def test_clear_cache():
    """
    Test clearing the cache.
    """
    logger = ReplayAttackLogger()
    
    request = {"user_id": 101, "action": "update"}
    
    signature = logger.log_request(request)
    assert signature in logger._cache
    
    logger.clear_cache()
    assert len(logger._cache) == 0