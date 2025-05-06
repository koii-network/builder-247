import time
import uuid
import statistics
from typing import List, Union

class TransactionIDValidator:
    """
    A performance benchmarking class for transaction ID validation.
    
    This class provides methods to generate, validate, and benchmark 
    transaction ID generation and validation processes.
    """
    
    @staticmethod
    def generate_transaction_id() -> str:
        """
        Generate a unique transaction ID using UUID.
        
        Returns:
            str: A unique transaction ID
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def validate_transaction_id(transaction_id: str) -> bool:
        """
        Validate a transaction ID.
        
        Args:
            transaction_id (str): The transaction ID to validate
        
        Returns:
            bool: True if the transaction ID is valid, False otherwise
        """
        try:
            # Validate that the transaction ID is a valid UUID
            uuid.UUID(str(transaction_id))
            return True
        except (ValueError, TypeError):
            return False
    
    def benchmark_transaction_id_generation(self, iterations: int = 1000) -> dict:
        """
        Benchmark the performance of transaction ID generation.
        
        Args:
            iterations (int, optional): Number of iterations to run. Defaults to 1000.
        
        Returns:
            dict: Performance metrics including min, max, mean, and median generation times
        """
        generation_times: List[float] = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            self.generate_transaction_id()
            end_time = time.perf_counter()
            generation_times.append(end_time - start_time)
        
        return {
            'min_time': min(generation_times),
            'max_time': max(generation_times),
            'mean_time': statistics.mean(generation_times),
            'median_time': statistics.median(generation_times),
            'iterations': iterations
        }
    
    def benchmark_transaction_id_validation(self, iterations: int = 1000) -> dict:
        """
        Benchmark the performance of transaction ID validation.
        
        Args:
            iterations (int, optional): Number of iterations to run. Defaults to 1000.
        
        Returns:
            dict: Performance metrics including min, max, mean, and median validation times
        """
        # Generate valid transaction IDs for testing
        valid_transaction_ids = [self.generate_transaction_id() for _ in range(iterations)]
        # Add some invalid transaction IDs
        invalid_transaction_ids = ['invalid_id', 'another_bad_id', '123']
        
        validation_times: List[float] = []
        
        # Mix of valid and invalid IDs
        test_ids = valid_transaction_ids + invalid_transaction_ids
        
        for transaction_id in test_ids:
            start_time = time.perf_counter()
            self.validate_transaction_id(transaction_id)
            end_time = time.perf_counter()
            validation_times.append(end_time - start_time)
        
        return {
            'min_time': min(validation_times),
            'max_time': max(validation_times),
            'mean_time': statistics.mean(validation_times),
            'median_time': statistics.median(validation_times),
            'iterations': len(test_ids)
        }