import concurrent.futures
import threading
import uuid
from typing import List, Set

import pytest

class TransactionIDGenerator:
    def __init__(self):
        self._generated_ids: Set[str] = set()
        self._lock = threading.Lock()

    def generate_unique_transaction_id(self) -> str:
        """
        Generate a unique transaction ID in a thread-safe manner.
        
        :return: A unique transaction ID
        :raises ValueError: If a duplicate transaction ID is generated
        """
        with self._lock:
            transaction_id = str(uuid.uuid4())
            
            # Ensure absolute uniqueness
            if transaction_id in self._generated_ids:
                raise ValueError(f"Duplicate transaction ID generated: {transaction_id}")
            
            self._generated_ids.add(transaction_id)
            return transaction_id

def test_concurrent_transaction_id_generation():
    """
    Test concurrent transaction ID generation to ensure uniqueness and thread safety.
    
    This test simulates multiple threads generating transaction IDs simultaneously
    and checks that:
    1. No duplicate IDs are generated
    2. All IDs are unique
    3. Concurrent generation doesn't cause race conditions
    """
    transaction_id_generator = TransactionIDGenerator()
    num_threads = 100
    generated_ids: List[str] = []

    def generate_id():
        try:
            return transaction_id_generator.generate_unique_transaction_id()
        except Exception as e:
            pytest.fail(f"Error generating transaction ID: {e}")

    # Use ThreadPoolExecutor to simulate concurrent ID generation
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(generate_id) for _ in range(num_threads)]
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            generated_ids.append(future.result())

    # Verify uniqueness
    assert len(generated_ids) == len(set(generated_ids)), "Duplicate transaction IDs generated"
    assert len(generated_ids) == num_threads, f"Expected {num_threads} unique IDs"

def test_transaction_id_generation_under_stress():
    """
    Stress test transaction ID generation with high concurrency.
    
    This test ensures the generator can handle a large number of concurrent requests
    without performance degradation or ID generation failures.
    """
    transaction_id_generator = TransactionIDGenerator()
    num_threads = 1000
    generated_ids: List[str] = []

    def generate_id():
        return transaction_id_generator.generate_unique_transaction_id()

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(generate_id) for _ in range(num_threads)]
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            generated_ids.append(future.result())

    # Verify uniqueness and count
    assert len(generated_ids) == len(set(generated_ids)), "Duplicate transaction IDs generated under stress"
    assert len(generated_ids) == num_threads, f"Expected {num_threads} unique IDs"

def test_transaction_id_generator_thread_safety():
    """
    Validate the thread-safety of the TransactionIDGenerator.
    
    This test checks that concurrent access doesn't lead to race conditions
    or inconsistent state in the ID generator.
    """
    transaction_id_generator = TransactionIDGenerator()
    num_threads = 50
    error_flag = threading.Event()

    def concurrent_generation():
        try:
            # Multiple rapid generations in a tight loop
            for _ in range(20):
                transaction_id = transaction_id_generator.generate_unique_transaction_id()
                assert transaction_id is not None, "Transaction ID cannot be None"
        except Exception as e:
            error_flag.set()
            pytest.fail(f"Error in concurrent generation: {e}")

    threads = [threading.Thread(target=concurrent_generation) for _ in range(num_threads)]
    
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert not error_flag.is_set(), "Thread-safety test failed"