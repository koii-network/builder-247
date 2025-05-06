import time
import uuid
from prometheus_swarm.utils.nonce import NonceTracker


def test_nonce_performance():
    """
    Performance test for nonce validation.
    Ensure each nonce validation takes less than 5ms.
    """
    tracker = NonceTracker()
    
    # Generate unique nonces to test
    nonces = [str(uuid.uuid4()) for _ in range(1000)]
    
    start_time = time.time()
    
    # Validate each nonce
    for nonce in nonces:
        result = tracker.is_nonce_valid(nonce)
        assert result == True, f"Nonce {nonce} should be valid"
    
    end_time = time.time()
    
    # Calculate total time and average time per nonce
    total_time = (end_time - start_time) * 1000  # Convert to milliseconds
    avg_time_per_nonce = total_time / len(nonces)
    
    print(f"\nTotal validation time: {total_time:.2f} ms")
    print(f"Average time per nonce: {avg_time_per_nonce:.2f} ms")
    
    # Assert average time is less than 5ms
    assert avg_time_per_nonce < 5, f"Average nonce validation time {avg_time_per_nonce:.2f} ms exceeds 5ms"