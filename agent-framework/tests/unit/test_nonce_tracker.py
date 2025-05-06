import pytest
import time
import threading
from prometheus_swarm.utils.nonce import NonceTracker

def test_generate_nonce_is_unique():
    """Test that generated nonces are unique."""
    tracker = NonceTracker()
    nonce1 = tracker.generate_nonce()
    nonce2 = tracker.generate_nonce()
    assert nonce1 != nonce2

def test_track_new_nonce():
    """Test tracking a new nonce returns True."""
    tracker = NonceTracker()
    nonce = tracker.generate_nonce()
    assert tracker.track_nonce(nonce) == True

def test_track_duplicate_nonce():
    """Test tracking a duplicate nonce returns False."""
    tracker = NonceTracker()
    nonce = tracker.generate_nonce()
    assert tracker.track_nonce(nonce) == True
    assert tracker.track_nonce(nonce) == False

def test_nonce_expiration():
    """Test that nonces expire after the specified time."""
    tracker = NonceTracker(expiration_time=1, cleanup_interval=0.5)
    nonce = tracker.generate_nonce()
    assert tracker.track_nonce(nonce) == True
    
    # Wait for nonce to expire
    time.sleep(1.5)
    
    # Nonce should now be trackable again
    assert tracker.track_nonce(nonce) == True

def test_thread_safety():
    """Test thread-safe nonce tracking."""
    tracker = NonceTracker()
    nonce = tracker.generate_nonce()
    
    def try_track_nonce():
        nonlocal results
        results.append(tracker.track_nonce(nonce))
    
    results = []
    threads = [threading.Thread(target=try_track_nonce) for _ in range(10)]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Only one thread should successfully track the nonce
    assert results.count(True) == 1
    assert results.count(False) == 9

def test_multiple_nonces():
    """Test tracking multiple different nonces."""
    tracker = NonceTracker()
    nonces = [tracker.generate_nonce() for _ in range(100)]
    
    # All nonces should be trackable initially
    for nonce in nonces:
        assert tracker.track_nonce(nonce) == True
    
    # Subsequent tracking should fail
    for nonce in nonces:
        assert tracker.track_nonce(nonce) == False

def test_nonce_cleanup():
    """Test automatic nonce cleanup."""
    tracker = NonceTracker(expiration_time=1, cleanup_interval=0.5)
    
    # Generate multiple nonces
    nonces = [tracker.generate_nonce() for _ in range(10)]
    
    # Track all nonces
    for nonce in nonces:
        assert tracker.track_nonce(nonce) == True
    
    # Wait for expiration and cleanup
    time.sleep(1.5)
    
    # All nonces should be trackable again
    for nonce in nonces:
        assert tracker.track_nonce(nonce) == True