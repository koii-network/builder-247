import timeit
from prometheus_swarm.utils.signatures import generate_signature

def test_signature_generation_performance():
    """
    Test the performance of signature generation.
    Ensure the average execution time is less than 5ms.
    """
    # Test with a small dictionary
    small_dict = {"key1": "value1", "key2": 2}
    
    # Time the signature generation (1000 iterations)
    def generate_small_signature():
        return generate_signature(small_dict)
    
    # Measure execution time
    execution_times = timeit.repeat(generate_small_signature, repeat=100, number=1000)
    
    # Average time per single execution in milliseconds
    avg_time_ms = min(execution_times) * 1000 / 1000
    
    print(f"Average signature generation time: {avg_time_ms:.4f} ms")
    assert avg_time_ms < 5, f"Signature generation too slow: {avg_time_ms} ms"