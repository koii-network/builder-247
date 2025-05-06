import time
import pytest
from prometheus_swarm.utils.nonce import NonceTracker

def test_nonce_generation():
    """Test that nonce generation creates unique nonces."""
    tracker = NonceTracker()
    
    # Generate multiple nonces
    nonce1 = tracker.generate_nonce()
    nonce2 = tracker.generate_nonce()
    
    assert nonce1 != nonce2, "Nonces should be unique"

def test_nonce_validation():
    """Test nonce validation mechanism."""
    tracker = NonceTracker(max_nonce_lifetime=5)
    
    # Generate a nonce
    nonce = tracker.generate_nonce()
    
    # First validation should pass
    assert tracker.validate_nonce(nonce) == True
    
    # Second validation of same nonce should fail
    assert tracker.validate_nonce(nonce) == False

def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    tracker = NonceTracker(max_nonce_lifetime=1)
    
    # Generate nonce
    nonce = tracker.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Nonce should now be invalid
    assert tracker.validate_nonce(nonce) == False

def test_remove_expired_nonces():
    """Test removing expired nonces."""
    tracker = NonceTracker(max_nonce_lifetime=1)
    
    # Generate multiple nonces
    nonce1 = tracker.generate_nonce()
    nonce2 = tracker.generate_nonce(data="extra")
    
    # Wait for nonces to expire
    time.sleep(2)
    
    # Call remove_expired_nonces
    tracker.remove_expired_nonces()
    
    # Validate that nonces are no longer in the tracker
    assert tracker.validate_nonce(nonce1) == False
    assert tracker.validate_nonce(nonce2) == False

def test_thread_safety():
    """Basic test to check thread safety of nonce generation."""
    import threading
    
    tracker = NonceTracker()
    nonces = set()
    
    def generate_and_store_nonce():
        nonce = tracker.generate_nonce()
        nonces.add(nonce)
    
    # Create multiple threads generating nonces
    threads = [threading.Thread(target=generate_and_store_nonce) for _ in range(100)]
    
    # Start threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # All nonces should be unique
    assert len(nonces) == 100, "Nonce generation should be thread-safe"

def test_nonce_with_data():
    """Test nonce generation with additional data."""
    tracker = NonceTracker()
    
    # Generate nonces with different data
    nonce1 = tracker.generate_nonce(data="request1")
    nonce2 = tracker.generate_nonce(data="request2")
    
    assert nonce1 != nonce2, "Nonces with different data should be unique"
    assert tracker.validate_nonce(nonce1) == True
    assert tracker.validate_nonce(nonce2) == True