import time
from prometheus_swarm.database.nonce import Nonce
from prometheus_swarm.database.nonce_storage import InMemoryNonceStorage

def test_nonce_lookup_performance():
    """Verify nonce lookup completes in less than 10ms."""
    storage = InMemoryNonceStorage()
    
    # Create 1000 nonces
    nonces = [Nonce() for _ in range(1000)]
    
    # Store all nonces
    for nonce in nonces:
        storage.store_nonce(nonce)
    
    # Measure lookup time for a specific nonce
    test_nonce = nonces[500]
    
    start_time = time.time()
    result = storage.get_nonce(test_nonce.value)
    end_time = time.time()
    
    lookup_time_ms = (end_time - start_time) * 1000
    
    assert result is not None
    assert lookup_time_ms < 10, f"Lookup took {lookup_time_ms}ms, expected < 10ms"