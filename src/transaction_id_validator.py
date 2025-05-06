import time
import uuid
import statistics
from typing import List, Tuple, Callable

class TransactionIDValidator:
    """
    A class for validating and benchmarking transaction ID validation performance.
    """

    @staticmethod
    def validate_transaction_id(transaction_id: str) -> bool:
        """
        Validate a transaction ID based on specific criteria.
        
        Args:
            transaction_id (str): The transaction ID to validate
        
        Returns:
            bool: True if the transaction ID is valid, False otherwise
        """
        # Basic validation criteria:
        # 1. Must be a valid UUID 
        # 2. Cannot be empty or None
        # 3. Must be a string
        try:
            if not transaction_id or not isinstance(transaction_id, str):
                return False
            
            # Attempt to parse as a valid UUID
            uuid.UUID(transaction_id)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def benchmark_validation(
        validation_func: Callable[[str], bool], 
        transaction_ids: List[str], 
        num_iterations: int = 1000
    ) -> Tuple[float, float, float]:
        """
        Benchmark the performance of a transaction ID validation function.
        
        Args:
            validation_func (Callable): The validation function to benchmark
            transaction_ids (List[str]): List of transaction IDs to validate
            num_iterations (int, optional): Number of times to run the benchmark. Defaults to 1000.
        
        Returns:
            Tuple[float, float, float]: (min time, max time, average time) in milliseconds
        """
        if not transaction_ids:
            raise ValueError("Transaction IDs list cannot be empty")
        
        times = []
        
        for _ in range(num_iterations):
            start_time = time.perf_counter()
            
            # Validate each transaction ID in the list
            for tx_id in transaction_ids:
                validation_func(tx_id)
            
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        return (
            min(times),  # Minimum time
            max(times),  # Maximum time
            statistics.mean(times)  # Average time
        )

    @staticmethod
    def generate_test_transaction_ids(num_ids: int = 100) -> List[str]:
        """
        Generate a list of random transaction IDs for testing.
        
        Args:
            num_ids (int, optional): Number of transaction IDs to generate. Defaults to 100.
        
        Returns:
            List[str]: List of generated transaction IDs
        """
        return [str(uuid.uuid4()) for _ in range(num_ids)]