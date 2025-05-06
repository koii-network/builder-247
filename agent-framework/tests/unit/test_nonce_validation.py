import time
import pytest
from prometheus_swarm.utils.nonce_validation import DistributedNonceValidator

def test_generate_nonce():
    """Test nonce generation creates unique identifiers."""
    validator = DistributedNonceValidator()
    
    # Generate multiple nonces and ensure they're unique
    nonce1 = validator.generate_nonce("test_data1")
    nonce2 = validator.generate_nonce("test_data2")
    nonce3 = validator.generate_nonce("test_data1")
    
    assert nonce1 != nonce2, "Nonces for different data should be unique"
    assert nonce1 != nonce3, "Nonces for same data should differ due to timestamp"

def test_nonce_validation():
    """Test basic nonce validation logic."""
    validator = DistributedNonceValidator(expiration_time=1)
    
    # Generate a nonce
    nonce = validator.generate_nonce("test_data")
    
    # First validation should succeed
    assert validator.validate_nonce(nonce), "First nonce validation should succeed"
    
    # Second validation should fail (replay protection)
    assert not validator.validate_nonce(nonce), "Second nonce validation should fail"

def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    validator = DistributedNonceValidator(expiration_time=0.1)
    
    # Generate nonce
    nonce = validator.generate_nonce("test_data")
    
    # First validation succeeds
    assert validator.validate_nonce(nonce), "First nonce validation should succeed"
    
    # Wait for expiration
    time.sleep(0.2)
    
    # Nonce should be reusable after expiration
    assert validator.validate_nonce(nonce), "Expired nonce should be reusable"

def test_nonce_max_limit():
    """Test maximum nonce limit handling."""
    validator = DistributedNonceValidator(expiration_time=3600, max_nonces=2)
    
    # Generate 3 nonces (exceeding max limit)
    nonce1 = validator.generate_nonce("test_data1")
    nonce2 = validator.generate_nonce("test_data2")
    nonce3 = validator.generate_nonce("test_data3")
    
    # First two should be valid
    assert validator.validate_nonce(nonce1), "First nonce should be valid"
    assert validator.validate_nonce(nonce2), "Second nonce should be valid"
    
    # Third nonce should fail due to max limit
    assert not validator.validate_nonce(nonce3), "Third nonce should fail due to max limit"

def test_nonce_stats():
    """Test nonce statistics."""
    validator = DistributedNonceValidator(expiration_time=1, max_nonces=5)
    
    # Generate some nonces
    nonces = [validator.generate_nonce(f"test_data_{i}") for i in range(3)]
    
    # Validate nonces
    for nonce in nonces:
        assert validator.validate_nonce(nonce), f"Nonce {nonce} should be valid"
    
    # Check stats
    stats = validator.get_nonce_stats()
    assert stats['total_nonces'] == 3, "Stats should reflect number of nonces"
    assert stats['max_nonces'] == 5, "Max nonces should match initialization"
    assert stats['expiration_time'] == 1, "Expiration time should match initialization"

def test_thread_safety():
    """Basic thread safety test."""
    import threading
    
    validator = DistributedNonceValidator()
    results = []
    
    def validate_nonce(nonce):
        results.append(validator.validate_nonce(nonce))
    
    # Generate a single nonce
    nonce = validator.generate_nonce("test_data")
    
    # Create multiple threads trying to validate same nonce
    threads = [
        threading.Thread(target=validate_nonce, args=(nonce,)) 
        for _ in range(10)
    ]
    
    # Start threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Only one thread should have succeeded
    assert results.count(True) == 1, "Only one thread should successfully validate"
    assert results.count(False) == 9, "Other threads should fail validation"