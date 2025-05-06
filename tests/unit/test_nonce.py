import pytest
import time
import re
import base64
from src.utils.nonce import generate_nonce

def test_nonce_generation_default():
    """Test default nonce generation."""
    nonce = generate_nonce()
    assert isinstance(nonce, str)
    assert len(nonce) == 43  # Exact length for default 43-byte nonce

def test_nonce_custom_length():
    """Test nonce generation with custom length."""
    lengths = [16, 32, 64, 128]
    for length in lengths:
        nonce = generate_nonce(length=length)
        assert len(nonce) == length
        base64.urlsafe_b64decode(nonce + '=' * (4 - len(nonce) % 4))  # Validate base64 decoding

def test_nonce_uniqueness():
    """Test that generated nonces are unique."""
    nonces = set(generate_nonce() for _ in range(1000))
    assert len(nonces) == 1000

def test_nonce_no_timestamp():
    """Test nonce generation without timestamp."""
    nonce = generate_nonce(include_timestamp=False)
    assert isinstance(nonce, str)
    assert len(nonce) == 43

def test_nonce_invalid_length():
    """Test invalid nonce length raises ValueError."""
    with pytest.raises(ValueError, match="Nonce length must be between 16 and 128 bytes"):
        generate_nonce(length=15)
    
    with pytest.raises(ValueError, match="Nonce length must be between 16 and 128 bytes"):
        generate_nonce(length=129)

def test_nonce_base64_encoding():
    """Test nonce is correctly base64 encoded."""
    nonce = generate_nonce()
    # Check base64 safe characters
    assert re.match(r'^[A-Za-z0-9_-]+={0,3}$', nonce)
    
    # Validate base64 decoding
    try:
        decoded = base64.urlsafe_b64decode(nonce + '=' * (4 - len(nonce) % 4))
        assert len(decoded) >= 16
    except Exception as e:
        pytest.fail(f"Invalid base64 encoding: {e}")

def test_nonce_randomness():
    """Test statistical randomness of nonce generation."""
    nonces = [generate_nonce() for _ in range(1000)]
    unique_nonces = set(nonces)
    
    # Check for extremely low collision probability
    assert len(unique_nonces) > 990