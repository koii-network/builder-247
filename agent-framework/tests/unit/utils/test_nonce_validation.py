import time
import pytest
from prometheus_swarm.utils.nonce_validation import DistributedNonceValidator

def test_nonce_generation():
    """Test that nonce generation creates unique identifiers."""
    validator = DistributedNonceValidator()
    nonce1 = validator.generate_nonce()
    nonce2 = validator.generate_nonce()
    
    assert nonce1 != nonce2, "Nonce generation should create unique identifiers"
    assert len(nonce1) > 0, "Nonce should not be an empty string"

def test_nonce_validation_basic():
    """Test basic nonce validation functionality."""
    validator = DistributedNonceValidator()
    nonce = validator.generate_nonce()
    
    # First validation should pass
    assert validator.validate_nonce(nonce) is True, "First nonce validation should succeed"
    
    # Second validation of the same nonce should fail
    assert validator.validate_nonce(nonce) is False, "Duplicate nonce should be rejected"

def test_nonce_expiration():
    """Test nonce expiration."""
    # Use a very short max_age to test expiration
    validator = DistributedNonceValidator(max_age=1)
    nonce = validator.generate_nonce()
    
    # First validate the nonce
    assert validator.validate_nonce(nonce) is True, "Initial nonce validation should succeed"
    
    # Wait for nonce to expire
    time.sleep(1.1)
    
    # Validating after expiration should succeed (as a new nonce)
    assert validator.validate_nonce(nonce) is True, "Expired nonce should be considered new"

def test_max_nonces_limit():
    """Test that the validator limits the number of stored nonces."""
    # Use a small max_nonces to test capacity management
    validator = DistributedNonceValidator(max_nonces=3)
    
    # Generate and validate more nonces than the max limit
    nonces = [validator.generate_nonce() for _ in range(5)]
    
    # Validate all nonces
    validation_results = [validator.validate_nonce(nonce) for nonce in nonces]
    
    # Verify that exactly max_nonces nonces can be stored
    assert sum(validation_results) == 3, "Should only validate up to max_nonces"

def test_concurrent_nonce_validation():
    """Simulate concurrent nonce validation scenarios."""
    import threading
    
    validator = DistributedNonceValidator()
    nonce = validator.generate_nonce()
    
    # Concurrent validation attempts
    def validate_nonce():
        nonlocal nonce
        return validator.validate_nonce(nonce)
    
    # Create multiple threads to validate the same nonce
    threads = [threading.Thread(target=validate_nonce) for _ in range(10)]
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Only the first validation should succeed
    assert validator.validate_nonce(nonce) is False, "Concurrent validation should work correctly"