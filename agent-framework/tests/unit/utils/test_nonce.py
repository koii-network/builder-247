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
    assert nonce_manager.validate_nonce(nonce) is True
    
    # Attempt to validate the same nonce again should raise an error
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
    
    # Verify only the latest 3 nonces are tracked
    for nonce in nonces[:2]:
        with pytest.raises(NonceAlreadyUsedError):
            nonce_manager.validate_nonce(nonce)
    
    for nonce in nonces[2:]:
        assert nonce_manager.validate_nonce(nonce) is True

def test_thread_safety():
    """Basic thread safety test."""
    from concurrent.futures import ThreadPoolExecutor
    
    nonce_manager = NonceManager()
    
    def generate_and_validate_nonce():
        nonce = nonce_manager.generate_nonce()
        return nonce_manager.validate_nonce(nonce)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: generate_and_validate_nonce(), range(100)))
    
    assert len(results) == 100, "All nonce generations should succeed"