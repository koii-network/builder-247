import time
import pytest
from src.nonce_service import NonceService

def test_generate_nonce():
    """Test that generated nonces are unique and non-empty."""
    service = NonceService()
    nonce1 = service.generate_nonce()
    nonce2 = service.generate_nonce()
    
    assert nonce1 is not None
    assert nonce2 is not None
    assert nonce1 != nonce2

def test_validate_nonce_basic():
    """Test basic nonce validation."""
    service = NonceService()
    nonce = service.generate_nonce()
    
    # First validation should succeed
    assert service.validate_nonce(nonce) is True
    
    # Second validation should fail (already used)
    assert service.validate_nonce(nonce) is False

def test_validate_nonce_different_instances():
    """Test nonce validation across different service instances."""
    service1 = NonceService()
    service2 = NonceService()
    
    nonce = service1.generate_nonce()
    
    # Another instance should recognize a used nonce
    assert service2.validate_nonce(nonce) is False

def test_nonce_expiration():
    """Test nonce expiration."""
    service = NonceService(max_age_seconds=1)
    nonce = service.generate_nonce()
    
    # Validate initial nonce
    assert service.validate_nonce(nonce) is True
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Nonce should now be considered expired
    assert service.validate_nonce(nonce) is True

def test_empty_nonce():
    """Test handling of empty or None nonce."""
    service = NonceService()
    
    assert service.validate_nonce(None) is False
    assert service.validate_nonce("") is False

def test_non_use_nonce_validation():
    """Test nonce validation without marking as used."""
    service = NonceService()
    nonce = service.generate_nonce()
    
    # First validation without using the nonce should succeed
    assert service.validate_nonce(nonce, use_nonce=False) is True
    
    # Second validation should also succeed
    assert service.validate_nonce(nonce, use_nonce=False) is True