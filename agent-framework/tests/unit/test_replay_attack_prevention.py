"""
Unit tests for Replay Attack Prevention Configuration
"""

import time
import pytest
from prometheus_swarm.security.replay_attack_prevention import ReplayAttackPreventionConfig

def test_validate_nonce_unique():
    """Test that unique nonces are validated"""
    config = ReplayAttackPreventionConfig()
    nonce1 = "unique_nonce_1"
    nonce2 = "unique_nonce_2"
    
    assert config.validate_nonce(nonce1) is True
    assert config.validate_nonce(nonce2) is True

def test_validate_nonce_duplicate():
    """Test that duplicate nonces are rejected"""
    config = ReplayAttackPreventionConfig()
    nonce = "duplicate_nonce"
    
    assert config.validate_nonce(nonce) is True
    assert config.validate_nonce(nonce) is False

def test_nonce_expiration():
    """Test that nonces expire after window size"""
    config = ReplayAttackPreventionConfig(window_size=1)
    nonce = "expiring_nonce"
    
    assert config.validate_nonce(nonce) is True
    
    # Mock time passing
    time.sleep(2)
    assert config.validate_nonce(nonce) is True

def test_max_nonce_cache_size():
    """Test that nonce cache respects max size"""
    config = ReplayAttackPreventionConfig(max_nonce_cache_size=2)
    
    nonce1 = "nonce1"
    nonce2 = "nonce2"
    nonce3 = "nonce3"
    
    assert config.validate_nonce(nonce1) is True
    assert config.validate_nonce(nonce2) is True
    assert config.validate_nonce(nonce3) is True

def test_set_window_size():
    """Test setting window size"""
    config = ReplayAttackPreventionConfig()
    
    config.set_window_size(600)
    assert config.get_config()['window_size'] == 600

def test_set_window_size_invalid():
    """Test setting invalid window size"""
    config = ReplayAttackPreventionConfig()
    
    with pytest.raises(ValueError):
        config.set_window_size(-100)

def test_set_max_nonce_cache_size():
    """Test setting max nonce cache size"""
    config = ReplayAttackPreventionConfig()
    
    config.set_max_nonce_cache_size(2000)
    assert config.get_config()['max_nonce_cache_size'] == 2000

def test_set_max_nonce_cache_size_invalid():
    """Test setting invalid max nonce cache size"""
    config = ReplayAttackPreventionConfig()
    
    with pytest.raises(ValueError):
        config.set_max_nonce_cache_size(-100)

def test_get_config():
    """Test retrieving configuration"""
    config = ReplayAttackPreventionConfig(
        window_size=300, 
        max_nonce_cache_size=1000
    )
    
    config_dict = config.get_config()
    
    assert config_dict['window_size'] == 300
    assert config_dict['max_nonce_cache_size'] == 1000
    assert 'current_nonce_count' in config_dict