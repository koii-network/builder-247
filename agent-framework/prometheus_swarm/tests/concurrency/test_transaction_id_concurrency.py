import threading
import queue
import uuid
import time
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed

class TransactionIDGenerator:
    """
    Thread-safe transaction ID generator to ensure unique IDs 
    across concurrent submissions.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._generated_ids = set()

    def generate_transaction_id(self) -> str:
        """
        Generate a unique transaction ID in a thread-safe manner.
        
        Returns:
            str: A unique transaction ID
        
        Raises:
            RuntimeError: If unable to generate a unique ID after multiple attempts
        """
        max_attempts = 10
        for _ in range(max_attempts):
            with self._lock:
                # Generate a UUID and convert to string
                new_id = str(uuid.uuid4())
                
                # Check for uniqueness
                if new_id not in self._generated_ids:
                    self._generated_ids.add(new_id)
                    return new_id
            
            # Small delay to reduce contention
            time.sleep(0.001)
        
        raise RuntimeError("Failed to generate unique transaction ID")

def test_transaction_id_concurrency():
    """
    Test concurrent transaction ID generation to ensure:
    1. No duplicate IDs are generated
    2. All threads can generate IDs successfully
    3. Thread-safety is maintained
    """
    generator = TransactionIDGenerator()
    num_threads = 100
    generated_ids = queue.Queue()

    def worker():
        """Worker thread to generate transaction IDs"""
        try:
            transaction_id = generator.generate_transaction_id()
            generated_ids.put(transaction_id)
        except Exception as e:
            generated_ids.put(str(e))

    # Use ThreadPoolExecutor for efficient concurrent execution
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_threads)]
        
        # Wait for all futures to complete
        for future in as_completed(futures):
            future.result()

    # Collect all generated IDs
    all_ids = []
    while not generated_ids.empty():
        all_ids.append(generated_ids.get())

    # Verify unique IDs
    assert len(all_ids) == num_threads, "Not all threads generated an ID"
    assert len(set(all_ids)) == num_threads, "Duplicate transaction IDs detected"

def test_transaction_id_generation_speed():
    """
    Test the performance of transaction ID generation under concurrent conditions.
    """
    generator = TransactionIDGenerator()
    start_time = time.time()
    
    def speed_worker():
        generator.generate_transaction_id()

    # Generate a large number of IDs concurrently
    with ThreadPoolExecutor(max_workers=50) as executor:
        list(executor.map(speed_worker, range(1000)))
    
    end_time = time.time()
    generation_time = end_time - start_time
    
    # Ensure IDs can be generated quickly (under 2 seconds for 1000 IDs)
    assert generation_time < 2, f"ID generation too slow: {generation_time} seconds"

def test_transaction_id_format():
    """
    Validate the format of generated transaction IDs.
    """
    generator = TransactionIDGenerator()
    transaction_id = generator.generate_transaction_id()
    
    # Verify UUID v4 format (36 characters including hyphens)
    assert len(transaction_id) == 36, "Invalid transaction ID length"
    assert transaction_id.count('-') == 4, "Invalid UUID format"