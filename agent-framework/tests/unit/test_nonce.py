import time
import pytest
from prometheus_swarm.utils.nonce import NonceService

def test_nonce_generation():
    """Test basic nonce generation"""
    nonce = NonceService.generate_nonce()
    assert nonce is not None
    assert len(nonce) > 0

def test_nonce_uniqueness():
    """Ensure different nonces are generated each time"""
    nonce1 = NonceService.generate_nonce()
    nonce2 = NonceService.generate_nonce()
    assert nonce1 != nonce2

def test_nonce_length_validation():
    """Test nonce length constraints"""
    nonce = NonceService.generate_nonce(length=32)
    assert len(nonce) > 0

    with pytest.raises(ValueError):
        NonceService.generate_nonce(length=10)  # Too short
    
    with pytest.raises(ValueError):
        NonceService.generate_nonce(length=100)  # Too long

def test_nonce_validation():
    """Test nonce validation"""
    nonce = NonceService.generate_nonce()
    assert NonceService.validate_nonce(nonce) is True

def test_nonce_expiration():
    """Test nonce expiration"""
    # Generate a nonce with a past timestamp
    past_time = time.time() - 7200  # 2 hours ago
    nonce = NonceService.generate_nonce(timestamp=past_time)
    
    # Default max_age is 1 hour, so this should be invalid
    assert NonceService.validate_nonce(nonce) is False

def test_invalid_nonce():
    """Test invalid nonce validation"""
    assert NonceService.validate_nonce('invalid_nonce') is False
    assert NonceService.validate_nonce('') is False

def test_custom_expiration():
    """Test custom nonce expiration"""
    nonce = NonceService.generate_nonce()
    
    # Validate with very short max_age
    assert NonceService.validate_nonce(nonce, max_age=0.1) is True
    
    # Wait briefly
    time.sleep(0.2)
    
    # Now it should be expired
    assert NonceService.validate_nonce(nonce, max_age=0.1) is False