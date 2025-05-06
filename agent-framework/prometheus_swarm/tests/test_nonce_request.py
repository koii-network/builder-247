import pytest
import time
from datetime import datetime, timedelta
from prometheus_swarm.nonce_request import NonceRequest

def test_generate_nonce():
    """Test that generate_nonce produces a unique nonce."""
    nonce_manager = NonceRequest()
    nonce1 = nonce_manager.generate_nonce()
    nonce2 = nonce_manager.generate_nonce()
    
    assert nonce1 != nonce2
    assert len(nonce1) > 0

def test_nonce_validation():
    """Test basic nonce validation."""
    nonce_manager = NonceRequest(duration=5)  # 5 seconds
    nonce = nonce_manager.generate_nonce()
    
    assert nonce_manager.validate_nonce(nonce) is True
    assert nonce_manager.validate_nonce(nonce) is False  # No reuse by default

def test_nonce_expiration():
    """Test nonce expiration."""
    nonce_manager = NonceRequest(duration=1)  # 1 second
    nonce = nonce_manager.generate_nonce()
    
    time.sleep(2)  # Wait beyond expiration
    assert nonce_manager.validate_nonce(nonce) is False

def test_nonce_context():
    """Test attaching and retrieving nonce context."""
    nonce_manager = NonceRequest()
    context = {"user_id": 123, "action": "login"}
    nonce = nonce_manager.generate_nonce(context)
    
    retrieved_context = nonce_manager.get_nonce_context(nonce)
    assert retrieved_context == context

def test_nonce_reuse_allowed():
    """Test nonce when reuse is explicitly allowed."""
    nonce_manager = NonceRequest(duration=5, allow_reuse=True)
    nonce = nonce_manager.generate_nonce()
    
    assert nonce_manager.validate_nonce(nonce) is True
    assert nonce_manager.validate_nonce(nonce) is True

def test_clear_expired_nonces():
    """Test clearing expired nonces."""
    nonce_manager = NonceRequest(duration=1)
    
    # Generate a few nonces
    nonce1 = nonce_manager.generate_nonce()
    nonce2 = nonce_manager.generate_nonce()
    
    time.sleep(2)  # Wait beyond expiration
    
    cleared_count = nonce_manager.clear_expired_nonces()
    assert cleared_count == 2

def test_invalid_nonce():
    """Test validation of an invalid/non-existent nonce."""
    nonce_manager = NonceRequest()
    assert nonce_manager.validate_nonce("invalid_nonce") is False