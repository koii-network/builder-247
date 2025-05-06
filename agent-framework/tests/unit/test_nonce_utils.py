import time
import pytest
from prometheus_swarm.utils.nonce import generate_nonce, validate_nonce, NonceError

def test_generate_nonce():
    """Test that a nonce can be generated."""
    nonce = generate_nonce()
    assert isinstance(nonce, str)
    assert len(nonce) > 0

def test_nonce_validation_success():
    """Test that a recently generated nonce is valid."""
    nonce = generate_nonce()
    assert validate_nonce(nonce) is True

def test_nonce_validation_expired():
    """Test that an expired nonce is rejected."""
    from unittest.mock import patch
    
    # Generate a nonce
    nonce = generate_nonce()
    
    # Simulate time passing beyond TTL
    with patch('time.time', return_value=time.time() + 7200):  # 2 hours later
        assert validate_nonce(nonce, max_ttl=3600) is False

def test_invalid_nonce_format():
    """Test handling of malformed nonces."""
    with pytest.raises(NonceError):
        validate_nonce("invalid_nonce")

def test_different_nonces_are_unique():
    """Ensure that generated nonces are unique."""
    nonce1 = generate_nonce()
    nonce2 = generate_nonce()
    assert nonce1 != nonce2

def test_nonce_custom_ttl():
    """Test nonce with a custom time-to-live."""
    nonce = generate_nonce(ttl=60)  # 1-minute TTL
    
    # Nonce should be valid before expiration
    assert validate_nonce(nonce, max_ttl=60) is True
    
    # Simulate time passing
    with patch('time.time', return_value=time.time() + 120):  # 2 minutes later
        assert validate_nonce(nonce, max_ttl=60) is False