import time
import pytest
from src.security.replay_attack_prevention import ReplayAttackPrevention

def test_generate_unique_tokens():
    """Test that generate_token creates unique tokens."""
    prevention = ReplayAttackPrevention()
    
    # Generate multiple tokens
    token1 = prevention.generate_token("data1")
    token2 = prevention.generate_token("data1")
    
    assert token1 != token2, "Tokens should be unique"

def test_token_validation():
    """Test basic token validation."""
    prevention = ReplayAttackPrevention()
    
    # Generate a token and validate
    token = prevention.generate_token("sensitive_data")
    assert prevention.validate_token(token), "Token should be valid first time"
    
    # Validate same token again (should fail)
    assert not prevention.validate_token(token), "Token should not be valid twice"

def test_token_expiration():
    """Test token expiration mechanism."""
    prevention = ReplayAttackPrevention(token_expiry_seconds=1)
    
    token = prevention.generate_token("test_data")
    assert prevention.validate_token(token), "Token should be valid initially"
    
    # Wait for token to expire
    time.sleep(1.5)
    
    # Reset the internal state to simulate time passing
    prevention._cleanup_expired_tokens(time.time())
    assert prevention.validate_token(token), "Expired token should become valid again"

def test_multiple_tokens():
    """Test handling multiple tokens."""
    prevention = ReplayAttackPrevention()
    
    tokens = [prevention.generate_token(f"data{i}") for i in range(5)]
    
    # First validation should work
    for token in tokens:
        assert prevention.validate_token(token), f"Token {token} should be valid"
    
    # Second validation should fail
    for token in tokens:
        assert not prevention.validate_token(token), f"Token {token} should not be valid twice"

def test_reset():
    """Test reset functionality."""
    prevention = ReplayAttackPrevention()
    
    # Generate and validate a token
    token = prevention.generate_token("reset_test")
    prevention.validate_token(token)
    
    # Reset and validate again
    prevention.reset()
    assert prevention.validate_token(token), "Token should be valid after reset"

def test_concurrent_token_generation():
    """Test token generation in quick succession."""
    prevention = ReplayAttackPrevention()
    
    token1 = prevention.generate_token("concurrent_data")
    token2 = prevention.generate_token("concurrent_data")
    
    assert token1 != token2, "Tokens generated in quick succession should be unique"