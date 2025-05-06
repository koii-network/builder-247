import time
import pytest
from src.nonce_service import NonceService

def test_generate_nonce_default_length():
    """Test default nonce generation"""
    nonce = NonceService.generate_nonce()
    assert len(nonce) == 64  # 32 bytes * 2 (hex representation)
    assert isinstance(nonce, str)

def test_generate_nonce_custom_length():
    """Test nonce generation with custom length"""
    nonce16 = NonceService.generate_nonce(16)
    nonce48 = NonceService.generate_nonce(48)
    
    assert len(nonce16) == 32  # 16 bytes * 2
    assert len(nonce48) == 96  # 48 bytes * 2

def test_generate_nonce_invalid_length():
    """Test nonce generation with invalid lengths"""
    with pytest.raises(ValueError):
        NonceService.generate_nonce(7)  # Too short
    
    with pytest.raises(ValueError):
        NonceService.generate_nonce(65)  # Too long

def test_unique_nonces():
    """Ensure generated nonces are unique"""
    nonce1 = NonceService.generate_nonce()
    nonce2 = NonceService.generate_nonce()
    
    assert nonce1 != nonce2

def test_time_based_nonce_generation():
    """Test time-based nonce generation"""
    nonce1 = NonceService.generate_time_based_nonce()
    time.sleep(0.1)  # Small delay
    nonce2 = NonceService.generate_time_based_nonce()
    
    assert nonce1 != nonce2

def test_time_based_nonce_verification():
    """Test verification of time-based nonces"""
    salt = "test_salt"
    nonce = NonceService.generate_time_based_nonce(salt)
    
    # Should be valid with current or near-current time
    time.sleep(0.1)  # Small delay
    assert NonceService.verify_time_based_nonce(nonce, salt) == True

def test_time_based_nonce_verification_expiry():
    """Test time-based nonce verification with expiry"""
    salt = "expiry_test"
    nonce = NonceService.generate_time_based_nonce(salt, max_age_seconds=1)
    
    time.sleep(2)  # Wait beyond max age
    
    # Should now be invalid
    assert NonceService.verify_time_based_nonce(nonce, salt, max_age_seconds=1) == False

def test_time_based_nonce_with_different_salts():
    """Test time-based nonce verification with different salts"""
    nonce = NonceService.generate_time_based_nonce("salt1")
    
    # Different salt should fail verification
    assert NonceService.verify_time_based_nonce(nonce, "salt2") == False