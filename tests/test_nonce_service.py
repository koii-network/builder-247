import pytest
import time
from src.nonce_service import NonceService

def test_generate_nonce_default():
    """Test default nonce generation"""
    nonce = NonceService.generate_nonce()
    assert len(nonce) == 32
    assert all(c in '0123456789abcdef' for c in nonce.lower())

def test_generate_nonce_custom_length():
    """Test nonce generation with custom length"""
    for length in [8, 16, 64, 128]:
        nonce = NonceService.generate_nonce(length=length)
        assert len(nonce) == length

def test_generate_nonce_without_timestamp():
    """Test nonce generation without timestamp"""
    nonce = NonceService.generate_nonce(include_timestamp=False)
    assert len(nonce) == 32

def test_generate_nonce_invalid_length():
    """Test nonce generation with invalid lengths"""
    with pytest.raises(ValueError):
        NonceService.generate_nonce(length=7)
    with pytest.raises(ValueError):
        NonceService.generate_nonce(length=129)

def test_validate_nonce_valid():
    """Test nonce validation for valid nonces"""
    nonce = NonceService.generate_nonce()
    assert NonceService.validate_nonce(nonce) is True

def test_validate_nonce_invalid_type():
    """Test nonce validation with invalid input types"""
    with pytest.raises(TypeError):
        NonceService.validate_nonce(123)
    with pytest.raises(TypeError):
        NonceService.validate_nonce(None)

def test_validate_nonce_invalid_format():
    """Test nonce validation with invalid format"""
    assert NonceService.validate_nonce('invalid nonce') is False
    assert NonceService.validate_nonce('!@#$%^&*') is False

def test_validate_nonce_expiration():
    """Test nonce validation with expiration"""
    class MockNonceService(NonceService):
        @staticmethod
        def generate_nonce(length=32, include_timestamp=True):
            # Generate a nonce with an old timestamp
            old_timestamp = str(int(time.time()) - 7200)  # 2 hours ago
            return 'a' * (length - len(old_timestamp)) + old_timestamp

    nonce = MockNonceService.generate_nonce()
    assert NonceService.validate_nonce(nonce, max_age=3600) is False

def test_nonce_uniqueness():
    """Test that generated nonces are unique"""
    nonces = set()
    for _ in range(100):
        nonce = NonceService.generate_nonce()
        assert nonce not in nonces
        nonces.add(nonce)