import time
import pytest
from src.nonce_validation import DistributedNonceValidator


def test_nonce_generation():
    """Test that nonce generation creates unique identifiers."""
    validator = DistributedNonceValidator()
    
    # Generate multiple nonces
    nonce1 = validator.generate_nonce()
    nonce2 = validator.generate_nonce()
    nonce3 = validator.generate_nonce('specific_context')
    
    # Ensure nonces are unique
    assert nonce1 != nonce2
    assert nonce1 != nonce3
    assert nonce2 != nonce3


def test_nonce_validation():
    """Test basic nonce validation."""
    validator = DistributedNonceValidator()
    
    # Generate and validate a nonce
    nonce = validator.generate_nonce()
    assert validator.validate_nonce(nonce) == True
    
    # Attempt to reuse the same nonce should fail
    assert validator.validate_nonce(nonce) == False


def test_nonce_context():
    """Test nonce validation with different contexts."""
    validator = DistributedNonceValidator()
    
    # Generate nonces with different contexts
    nonce1 = validator.generate_nonce('context1')
    nonce2 = validator.generate_nonce('context2')
    
    # Validate nonces 
    assert validator.validate_nonce(nonce1) == True
    assert validator.validate_nonce(nonce2) == True
    
    # Context does not affect nonce validation
    assert validator.validate_nonce(nonce1) == False


def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    # Create validator with very short expiration for testing
    validator = DistributedNonceValidator(expiration_time=1)
    
    # Generate a nonce
    nonce = validator.generate_nonce()
    assert validator.validate_nonce(nonce) == True
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Nonce should now be valid again after expiration
    assert validator.validate_nonce(nonce) == True


def test_multiple_nonce_validations():
    """Test multiple nonce generations and validations."""
    validator = DistributedNonceValidator()
    
    # Generate and validate multiple nonces
    nonces = [validator.generate_nonce() for _ in range(10)]
    
    # Validate all nonces once
    for nonce in nonces:
        assert validator.validate_nonce(nonce) == True
    
    # Attempt to reuse all nonces (should fail)
    for nonce in nonces:
        assert validator.validate_nonce(nonce) == False


def test_nonce_validation_thread_safety():
    """
    Simulate potential race conditions by generating many nonces 
    in quick succession.
    """
    validator = DistributedNonceValidator()
    
    # Generate many nonces in a tight loop
    nonces = set()
    for _ in range(1000):
        nonce = validator.generate_nonce()
        assert nonce not in nonces, "Duplicate nonce generated"
        nonces.add(nonce)
        assert validator.validate_nonce(nonce) == True