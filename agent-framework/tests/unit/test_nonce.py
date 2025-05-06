import time
import pytest
from prometheus_swarm.utils.nonce import NonceService

def test_nonce_generation():
    """Test basic nonce generation"""
    nonce_service = NonceService()
    nonce = nonce_service.generate_nonce()
    
    assert len(nonce) == 32
    assert isinstance(nonce, str)

def test_nonce_validation():
    """Test nonce validation with default settings"""
    nonce_service = NonceService(include_timestamp=True)
    nonce = nonce_service.generate_nonce()
    
    assert nonce_service.validate_nonce(nonce) is True

def test_nonce_custom_length():
    """Test nonce generation with custom length"""
    nonce_service = NonceService(length=64)
    nonce = nonce_service.generate_nonce()
    
    assert len(nonce) == 64

def test_nonce_with_salt():
    """Test nonce generation with salt"""
    nonce_service = NonceService(salt='test_salt')
    nonce1 = nonce_service.generate_nonce()
    nonce2 = nonce_service.generate_nonce()
    
    assert nonce1 != nonce2

def test_nonce_expiration():
    """Test nonce expiration"""
    nonce_service = NonceService(include_timestamp=True, max_age=1)
    base_time = time.time()
    nonce = nonce_service.generate_nonce(current_time=base_time)
    
    # Validate within valid time window
    assert nonce_service.validate_nonce(nonce, current_time=base_time) is True
    
    # Validate after expiration
    assert nonce_service.validate_nonce(nonce, current_time=base_time + 2) is False

def test_invalid_nonce_length():
    """Test invalid nonce length"""
    with pytest.raises(ValueError):
        NonceService(length=10)

def test_nonce_uniqueness():
    """Test that generated nonces are unique"""
    nonce_service = NonceService()
    nonces = set()
    
    for _ in range(100):
        nonce = nonce_service.generate_nonce()
        assert nonce not in nonces
        nonces.add(nonce)

def test_invalid_nonce_validation():
    """Test validation of invalid nonces"""
    nonce_service = NonceService()
    
    assert nonce_service.validate_nonce('') is False
    assert nonce_service.validate_nonce('short') is False
    assert nonce_service.validate_nonce('a' * 32) is False