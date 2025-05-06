import pytest
import time
import base64
import re

from prometheus_swarm.utils.nonce import generate_nonce

def test_generate_nonce_default():
    """Test default nonce generation"""
    nonce = generate_nonce()
    
    # Check basic properties
    assert isinstance(nonce, str)
    assert len(nonce) > 0
    
    # Verify base64 URL-safe encoding
    assert re.match(r'^[A-Za-z0-9_-]+$', nonce)

def test_generate_nonce_length():
    """Test nonce generation with different lengths"""
    # Test valid lengths
    for length in [16, 32, 48, 64]:
        nonce = generate_nonce(length=length)
        assert len(base64.urlsafe_b64decode(nonce + '==')) <= 64
    
    # Test invalid lengths
    with pytest.raises(ValueError):
        generate_nonce(length=15)
    with pytest.raises(ValueError):
        generate_nonce(length=65)

def test_generate_nonce_uniqueness():
    """Test that generated nonces are unique"""
    nonce1 = generate_nonce()
    nonce2 = generate_nonce()
    
    assert nonce1 != nonce2

def test_generate_nonce_timestamp_option():
    """Test nonce generation with and without timestamp"""
    # With timestamp (default)
    nonce_with_timestamp = generate_nonce(include_timestamp=True)
    assert nonce_with_timestamp is not None
    
    # Without timestamp
    nonce_without_timestamp = generate_nonce(include_timestamp=False)
    assert nonce_without_timestamp is not None

def test_nonce_randomness():
    """Test statistical randomness of nonce generation"""
    # Generate multiple nonces and check for uniqueness
    nonces = set(generate_nonce() for _ in range(1000))
    assert len(nonces) == 1000  # Highly unlikely to have duplicates

def test_nonce_encoding():
    """Test nonce base64 URL-safe encoding"""
    nonce = generate_nonce()
    
    # Verify it can be decoded
    try:
        decoded = base64.urlsafe_b64decode(nonce + '==')
    except Exception as e:
        pytest.fail(f"Nonce could not be decoded: {e}")
    
    # Verify decoded length
    assert len(decoded) in [32, 40]  # With/without timestamp