import time
import pytest
from prometheus_swarm.utils.nonce import NonceSecurityManager

def test_nonce_generation():
    """Test nonce generation produces unique and sufficiently long nonces."""
    nonce_manager = NonceSecurityManager()
    
    # Generate multiple nonces
    nonces = [nonce_manager.generate_nonce() for _ in range(100)]
    
    # Check uniqueness
    assert len(set(nonces)) == 100
    
    # Check default length (32 bytes = 64 hex characters)
    assert all(len(nonce) == 64 for nonce in nonces)

def test_nonce_validation():
    """Test nonce validation ensures each nonce is used only once."""
    nonce_manager = NonceSecurityManager(nonce_expiry_seconds=1)
    
    # First use of nonce should be valid
    nonce1 = nonce_manager.generate_nonce()
    assert nonce_manager.validate_nonce(nonce1) is True
    
    # Second use of same nonce should be invalid
    assert nonce_manager.validate_nonce(nonce1) is False

def test_nonce_expiry():
    """Test that nonces expire after the specified time."""
    nonce_manager = NonceSecurityManager(nonce_expiry_seconds=0.1)
    
    nonce = nonce_manager.generate_nonce()
    assert nonce_manager.validate_nonce(nonce) is True
    
    # Wait for nonce to expire
    time.sleep(0.2)
    
    # Nonce should now be considered expired and allow reuse
    assert nonce_manager.validate_nonce(nonce) is True

def test_nonce_age():
    """Test getting the age of a nonce."""
    nonce_manager = NonceSecurityManager(nonce_expiry_seconds=1)
    
    nonce = nonce_manager.generate_nonce()
    time.sleep(0.5)
    
    age = nonce_manager.get_nonce_age(nonce)
    assert 0.4 <= age <= 0.6  # Allow for slight timing variations

def test_concurrent_nonce_handling():
    """Simulate basic thread-safe behavior of nonce manager."""
    from concurrent.futures import ThreadPoolExecutor
    
    nonce_manager = NonceSecurityManager()
    
    def validate_unique_nonce(nonce):
        return nonce_manager.validate_nonce(nonce)
    
    # Generate many nonces concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        nonces = [nonce_manager.generate_nonce() for _ in range(100)]
        results = list(executor.map(validate_unique_nonce, nonces))
    
    # All nonces should be unique when first validated
    assert results.count(True) == 100

def test_clear_nonces():
    """Test manually clearing all nonces."""
    nonce_manager = NonceSecurityManager()
    
    # Generate and validate some nonces
    nonces = [nonce_manager.generate_nonce() for _ in range(5)]
    for nonce in nonces:
        assert nonce_manager.validate_nonce(nonce) is True
    
    # Clear nonces
    nonce_manager.clear_nonces()
    
    # All nonces should be valid again
    for nonce in nonces:
        assert nonce_manager.validate_nonce(nonce) is True