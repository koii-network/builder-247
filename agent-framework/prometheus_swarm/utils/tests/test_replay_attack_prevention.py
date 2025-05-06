import time
import pytest
from prometheus_swarm.utils.replay_attack_prevention import ReplayAttackPrevention, replay_attack_prevention

def test_token_generation():
    """Test basic token generation"""
    rap = ReplayAttackPrevention()
    token1 = rap.generate_token()
    token2 = rap.generate_token()
    
    assert token1 != token2
    assert len(token1) == 64  # SHA-256 hash length
    assert len(token2) == 64

def test_token_validation():
    """Test token validation and single-use mechanism"""
    rap = ReplayAttackPrevention()
    token = rap.generate_token()
    
    # First validation should succeed
    assert rap.validate_token(token) is True
    
    # Second validation of the same token should fail
    assert rap.validate_token(token) is False

def test_token_expiration():
    """Test token expiration"""
    rap = ReplayAttackPrevention(max_token_age=1)
    token = rap.generate_token()
    
    # Wait for token to expire
    time.sleep(2)
    
    # Token should be considered invalid after expiration
    assert rap.validate_token(token) is False

def test_token_max_tokens():
    """Test maximum token limit"""
    rap = ReplayAttackPrevention(max_tokens=2)
    
    # Generate more tokens than max_tokens
    tokens = [rap.generate_token(i) for i in range(5)]
    
    # Check that only the most recent tokens are kept
    assert len(rap._tokens) == 2

def test_configuration():
    """Test configuration of replay attack prevention"""
    rap = ReplayAttackPrevention()
    
    # Initial configuration
    initial_config = rap.get_config()
    assert initial_config['enabled'] is True
    assert initial_config['max_token_age'] == 300
    assert initial_config['max_tokens'] == 1000
    
    # Update configuration
    rap.configure(
        max_token_age=600,
        max_tokens=500,
        enabled=False
    )
    
    updated_config = rap.get_config()
    assert updated_config['enabled'] is False
    assert updated_config['max_token_age'] == 600
    assert updated_config['max_tokens'] == 500

def test_disabled_prevention():
    """Test replay attack prevention when disabled"""
    rap = ReplayAttackPrevention(enabled=False)
    
    token = rap.generate_token()
    assert token == ""
    assert rap.validate_token("anytoken") is True

def test_global_singleton():
    """Test the global singleton instance"""
    replay_attack_prevention.configure(max_token_age=100)
    
    config = replay_attack_prevention.get_config()
    assert config['max_token_age'] == 100

def test_payload_based_token():
    """Test token generation with payload"""
    rap = ReplayAttackPrevention()
    
    token1 = rap.generate_token("payload1")
    token2 = rap.generate_token("payload2")
    
    assert token1 != token2