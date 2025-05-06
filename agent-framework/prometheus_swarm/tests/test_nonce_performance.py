"""Performance test for NonceTracker"""

import time
import pytest
from prometheus_swarm.utils.nonce import NonceTracker


def test_nonce_performance():
    """
    Verify nonce validation performance.
    Ensure each validation takes less than 5ms.
    """
    tracker = NonceTracker()
    
    # Generate multiple nonces
    nonces = [tracker.generate_nonce() for _ in range(100)]
    
    # Measure validation time
    start_time = time.time()
    for nonce in nonces:
        assert tracker.validate_nonce(nonce) is True
    end_time = time.time()
    
    # Calculate total time and per-nonce time
    total_time = (end_time - start_time) * 1000  # Convert to milliseconds
    per_nonce_time = total_time / len(nonces)
    
    print(f"\nTotal validation time: {total_time:.2f}ms")
    print(f"Per-nonce validation time: {per_nonce_time:.2f}ms")
    
    # Assert performance requirement
    assert per_nonce_time < 5, f"Nonce validation too slow: {per_nonce_time:.2f}ms"