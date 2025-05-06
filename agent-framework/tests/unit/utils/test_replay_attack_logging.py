import time
import pytest
from prometheus_swarm.utils.replay_attack_logging import ReplayAttackLogger

def test_replay_attack_logger_initialization():
    """Test that the ReplayAttackLogger can be initialized with default parameters."""
    logger = ReplayAttackLogger()
    assert isinstance(logger, ReplayAttackLogger)

def test_generate_signature():
    """Test that generate_signature creates unique signatures for different requests."""
    logger = ReplayAttackLogger()
    
    request1 = {"user_id": 123, "action": "login"}
    request2 = {"user_id": 456, "action": "logout"}
    
    signature1 = logger.generate_signature(request1)
    signature2 = logger.generate_signature(request2)
    
    assert signature1 != signature2
    assert len(signature1) == 64  # SHA-256 hash length
    assert len(signature2) == 64

def test_is_request_unique():
    """Test that unique and duplicate requests are correctly identified."""
    logger = ReplayAttackLogger()
    
    request = {"user_id": 123, "action": "login"}
    signature = logger.generate_signature(request)
    
    # First request should be unique
    assert logger.is_request_unique(signature) is True
    
    # Same signature should now be considered a duplicate
    assert logger.is_request_unique(signature) is False

def test_signature_expiration():
    """Test that signatures expire after the specified time."""
    logger = ReplayAttackLogger(max_cache_size=10, expiration_time=1)
    
    request = {"user_id": 123, "action": "login"}
    signature = logger.generate_signature(request)
    
    # First request is unique
    assert logger.is_request_unique(signature) is True
    
    # Duplicate request immediately after is not unique
    assert logger.is_request_unique(signature) is False
    
    # Wait for expiration
    time.sleep(1.1)
    
    # After expiration, the signature becomes unique again
    assert logger.is_request_unique(signature) is True

def test_max_cache_size():
    """Test that the cache respects the maximum size limit."""
    logger = ReplayAttackLogger(max_cache_size=3)
    
    # Create more signatures than the max cache size
    signatures = []
    for i in range(5):
        request = {"user_id": i, "action": "login"}
        signature = logger.generate_signature(request)
        logger.is_request_unique(signature)
        signatures.append(signature)
    
    # Only the last 3 signatures should remain
    assert len(logger._signature_cache) == 3
    assert signatures[2] in logger._signature_cache
    assert signatures[3] in logger._signature_cache
    assert signatures[4] in logger._signature_cache
    
    # First two signatures should have been dropped
    assert signatures[0] not in logger._signature_cache
    assert signatures[1] not in logger._signature_cache