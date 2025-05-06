import timeit
from src.signature_generator import generate_signature

def test_signature_generation_performance():
    data = {"name": "John", "age": 30, "city": "New York"}
    
    # Measure performance
    execution_time = timeit.timeit(
        lambda: generate_signature(data), 
        number=1000
    ) / 1000  # Average time per execution
    
    print(f"Average signature generation time: {execution_time * 1000:.4f} ms")
    assert execution_time * 1000 < 5, "Signature generation time exceeds 5ms"

if __name__ == "__main__":
    test_signature_generation_performance()