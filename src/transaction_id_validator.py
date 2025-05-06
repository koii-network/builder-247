import time
import uuid
import statistics
from typing import List, Callable, Any

class TransactionIDValidator:
    """
    A class for validating and benchmarking transaction ID validation.
    """
    
    @staticmethod
    def validate_transaction_id(transaction_id: Any) -> bool:
        """
        Validate a transaction ID.
        
        Args:
            transaction_id (Any): The transaction ID to validate.
        
        Returns:
            bool: True if the transaction ID is a valid UUID, False otherwise.
        """
        if not isinstance(transaction_id, str):
            return False
        
        try:
            # Stricter validation: ensure perfect UUID format
            uuid_obj = uuid.UUID(transaction_id)
            
            # Additional checks to ensure it's a canonical representation
            return str(uuid_obj) == transaction_id
        except (ValueError, TypeError, AttributeError):
            return False
    
    @staticmethod
    def benchmark_validation(
        validation_func: Callable[[Any], bool], 
        test_cases: List[Any], 
        num_iterations: int = 1000
    ) -> dict:
        """
        Benchmark the performance of a validation function.
        
        Args:
            validation_func (Callable): The validation function to benchmark.
            test_cases (List): A list of test cases to validate.
            num_iterations (int, optional): Number of times to run the benchmark. Defaults to 1000.
        
        Returns:
            dict: A dictionary containing performance metrics.
        """
        execution_times = []
        
        for _ in range(num_iterations):
            start_time = time.perf_counter()
            
            # Validate all test cases
            results = [validation_func(case) for case in test_cases]
            
            end_time = time.perf_counter()
            execution_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        return {
            'mean_time_ms': statistics.mean(execution_times),
            'median_time_ms': statistics.median(execution_times),
            'min_time_ms': min(execution_times),
            'max_time_ms': max(execution_times),
            'std_dev_ms': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            'total_test_cases': len(test_cases),
            'valid_cases': sum(results)
        }