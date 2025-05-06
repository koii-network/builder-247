import time
import pytest
from prometheus_swarm.utils.nonce_validation import DistributedNonceValidator

def test_nonce_validation_latency():
    """Test that nonce validation occurs within 20ms."""
    validator = DistributedNonceValidator()
    
    # Generate nonce
    nonce = validator.generate_nonce()
    
    # Measure validation time
    start_time = time.time()
    validator.validate_nonce(nonce)
    end_time = time.time()
    
    # Calculate latency in milliseconds
    latency_ms = (end_time - start_time) * 1000
    
    assert latency_ms <= 20, f"Nonce validation latency {latency_ms}ms exceeds 20ms threshold"