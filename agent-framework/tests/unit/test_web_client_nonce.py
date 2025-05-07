import pytest
from prometheus_swarm.clients.web_client_nonce import WebClientNonceManager

def test_generate_nonce_default_length():
    """Test nonce generation with default length."""
    nonce = WebClientNonceManager.generate_nonce()
    assert len(nonce) == 32
    assert WebClientNonceManager.validate_nonce(nonce)

def test_generate_nonce_custom_length():
    """Test nonce generation with custom length."""
    for length in [16, 24, 48, 64]:
        nonce = WebClientNonceManager.generate_nonce(length)
        assert len(nonce) == length
        assert WebClientNonceManager.validate_nonce(nonce)

def test_generate_nonce_invalid_length():
    """Test nonce generation fails for too short nonces."""
    with pytest.raises(ValueError):
        WebClientNonceManager.generate_nonce(15)

def test_nonce_uniqueness():
    """Verify generated nonces are unique."""
    nonces = set(WebClientNonceManager.generate_nonce() for _ in range(100))
    assert len(nonces) == 100

def test_nonce_validation():
    """Test nonce validation with various inputs."""
    # Valid nonces
    valid_cases = [
        WebClientNonceManager.generate_nonce(),
        WebClientNonceManager.generate_nonce(16),
        WebClientNonceManager.generate_nonce(64)
    ]
    
    # Invalid nonces
    invalid_cases = [
        None,
        "",  # Empty string
        "short",  # Too short
        "x" * 65,  # Too long
        "invalid-nonce!",  # Special characters
        "UPPERCASE_ONLY",  # Case sensitivity
        "   spaces   "
    ]
    
    for nonce in valid_cases:
        assert WebClientNonceManager.validate_nonce(nonce), f"Failed to validate: {nonce}"
    
    for nonce in invalid_cases:
        assert not WebClientNonceManager.validate_nonce(nonce), f"Incorrectly validated: {nonce}"