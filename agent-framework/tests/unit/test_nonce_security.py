"""
Tests for Nonce Security Configuration Module
"""

import time
import pytest
from prometheus_swarm.utils.nonce_security import NonceSecurityConfig


def test_nonce_generation():
    """Test nonce generation creates unique nonces."""
    config = NonceSecurityConfig()
    nonce1 = config.generate_nonce()
    nonce2 = config.generate_nonce()
    
    assert nonce1 != nonce2, "Generated nonces should be unique"
    assert len(nonce1) > 0, "Nonce should not be empty"


def test_nonce_validation_without_reuse():
    """Test nonce validation when reuse is not allowed."""
    config = NonceSecurityConfig(allow_reuse=False)
    
    nonce = config.generate_nonce()
    
    # First validation should pass
    assert config.validate_nonce(nonce), "First nonce validation should pass"
    
    # Second validation should fail
    assert not config.validate_nonce(nonce), "Reused nonce should be rejected"


def test_nonce_validation_with_reuse():
    """Test nonce validation when reuse is allowed."""
    config = NonceSecurityConfig(allow_reuse=True)
    
    nonce = config.generate_nonce()
    
    # Multiple validations should pass
    assert config.validate_nonce(nonce)
    assert config.validate_nonce(nonce)
    assert config.validate_nonce(nonce)


def test_nonce_expiration():
    """Test nonce expiration."""
    config = NonceSecurityConfig(
        nonce_expiration=1,  # 1 second expiration
        allow_reuse=False
    )
    
    nonce = config.generate_nonce()
    
    # First validation passes
    assert config.validate_nonce(nonce)
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Nonce should now be allowed again
    assert config.validate_nonce(nonce), "Expired nonce should be allowed after timeout"


def test_nonce_max_history():
    """Test maximum nonce history tracking."""
    config = NonceSecurityConfig(
        allow_reuse=False,
        max_nonce_history=3
    )
    
    # Generate and validate more nonces than max history
    nonces = [config.generate_nonce() for _ in range(5)]
    
    for nonce in nonces:
        config.validate_nonce(nonce)
    
    # Verify configuration
    config_details = config.get_configuration()
    assert config_details['max_nonce_history'] == 3
    assert config_details['allow_reuse'] == False


def test_configuration_retrieval():
    """Test retrieving nonce security configuration."""
    config = NonceSecurityConfig(
        nonce_length=16,
        nonce_expiration=7200,
        allow_reuse=True,
        max_nonce_history=500
    )
    
    details = config.get_configuration()
    
    assert details['nonce_length'] == 16
    assert details['nonce_expiration'] == 7200
    assert details['allow_reuse'] == True
    assert details['max_nonce_history'] == 500