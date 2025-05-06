import time
import threading
import pytest
from prometheus_swarm.utils.nonce import NonceTracker


def test_nonce_tracker_unique_nonce():
    """Test that unique nonces are accepted."""
    tracker = NonceTracker()
    
    assert tracker.is_nonce_valid("nonce1") == True
    assert tracker.is_nonce_valid("nonce1") == False  # Duplicate nonce
    assert tracker.is_nonce_valid("nonce2") == True


def test_nonce_tracker_thread_safety():
    """Test thread-safe nonce tracking."""
    tracker = NonceTracker()
    results = []
    
    def check_nonce(nonce):
        results.append(tracker.is_nonce_valid(nonce))
    
    # Create multiple threads trying to validate the same nonce
    threads = [
        threading.Thread(target=check_nonce, args=("shared_nonce",)) 
        for _ in range(10)
    ]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Only one thread should return True
    assert results.count(True) == 1
    assert results.count(False) == 9


def test_nonce_tracker_expiration():
    """Test nonce expiration."""
    # Short expiration time for testing
    tracker = NonceTracker(expiration_time=1)
    
    assert tracker.is_nonce_valid("test_nonce") == True
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Nonce should be valid again after expiration
    assert tracker.is_nonce_valid("test_nonce") == True


def test_nonce_tracker_set_expiration():
    """Test setting new expiration time."""
    tracker = NonceTracker(expiration_time=5)
    
    # First use the nonce
    assert tracker.is_nonce_valid("test_nonce1") == True
    
    # Change expiration time 
    tracker.set_expiration_time(1)
    
    # Wait just over 1 second
    time.sleep(1.1)
    
    # Nonce should now be invalid after first use and short expiration
    assert tracker.is_nonce_valid("test_nonce1") == True  # New nonce after expiration


def test_nonce_tracker_clear():
    """Test clearing all nonces."""
    tracker = NonceTracker()
    
    tracker.is_nonce_valid("nonce1")
    tracker.is_nonce_valid("nonce2")
    
    tracker.clear()
    
    # Both nonces should be valid again after clear
    assert tracker.is_nonce_valid("nonce1") == True
    assert tracker.is_nonce_valid("nonce2") == True