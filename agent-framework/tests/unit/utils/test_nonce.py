import time
import pytest
from prometheus_swarm.utils.nonce import NonceManager, NonceAlreadyUsedError, NonceExpiredError

def test_nonce_generation():
    """Test that nonces are generated uniquely."""
    nonce_manager = NonceManager()
    nonce1 = nonce_manager.generate_nonce()
    nonce2 = nonce_manager.generate_nonce()
    
    assert nonce1 != nonce2, "Nonces should be unique"

def test_nonce_validation():
    """Test nonce validation process."""
    nonce_manager = NonceManager()
    
    # Generate and validate a nonce
    nonce = nonce_manager.generate_nonce()
    nonce_manager.validate_nonce(nonce)
    
    # Attempting to validate the same nonce again should raise an error
    with pytest.raises(NonceAlreadyUsedError):
        nonce_manager.validate_nonce(nonce)

def test_nonce_validation_without_consume():
    """Test nonce validation without consuming the nonce."""
    nonce_manager = NonceManager()
    
    # Generate a nonce
    nonce = nonce_manager.generate_nonce()
    
    # Validate without consuming first
    assert nonce_manager.validate_nonce(nonce, consume=False) is True
    
    # Second validation should raise an error
    with pytest.raises(NonceAlreadyUsedError):
        nonce_manager.validate_nonce(nonce)

def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    # Create a nonce manager with very short expiry for testing
    nonce_manager = NonceManager(nonce_expiry=1)
    
    nonce = nonce_manager.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Validate should now generate a new valid nonce
    assert nonce_manager.validate_nonce(nonce) is True

def test_nonce_max_limit():
    """Test that nonce tracking respects the maximum limit."""
    nonce_manager = NonceManager(max_nonces=3)
    
    # Generate more nonces than the max limit
    nonces = [nonce_manager.generate_nonce() for _ in range(5)]
    
    # Verify the oldest nonces are removed
    for nonce in nonces[:2]:
        with pytest.raises(NonceAlreadyUsedError):
            nonce_manager.validate_nonce(nonce)
    
    for nonce in nonces[2:]:
        assert nonce_manager.validate_nonce(nonce) is True

def test_thread_safety():
    """Basic thread safety test."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    nonce_manager = NonceManager()
    
    def generate_and_validate_nonce():
        nonce = nonce_manager.generate_nonce()
        return nonce_manager.validate_nonce(nonce)
    
    # Use as_completed to handle potential exceptions
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(generate_and_validate_nonce) for _ in range(100)]
        
        # Wait for all futures to complete
        for future in as_completed(futures):
            assert future.result() is True