import time
import uuid
import re
import statistics
from typing import List, Callable, Any

class TransactionIDValidator:
    """
    A class for validating and benchmarking transaction ID validation.
    """
    
    @staticmethod
    def validate_transaction_id(transaction_id: Any) -> bool:
        """
        Validate a transaction ID with comprehensive checks.
        
        Args:
            transaction_id (Any): The transaction ID to validate.
        
        Returns:
            bool: True if the transaction ID is a valid UUID, False otherwise.
        """
        # First, check if it's a string
        if not isinstance(transaction_id, str):
            return False
        
        # Ensure consistent lowercase for comparison
        transaction_id = transaction_id.lower()
        
        # First, check the overall structure of the UUID
        # Validate each segment of the UUID
        segments = transaction_id.split('-')
        if len(segments) != 5:
            return False
        
        # Check lengths of each UUID segment
        if (len(segments[0]) != 8 or 
            len(segments[1]) != 4 or 
            len(segments[2]) != 4 or 
            len(segments[3]) != 4 or 
            len(segments[4]) != 12):
            return False
        
        # Check if all characters are valid hex
        if not all(
            all(c in '0123456789abcdef' for c in segment) 
            for segment in segments
        ):
            return False
        
        # Use uuid library for final validation
        try:
            parsed_uuid = uuid.UUID(transaction_id)
            # Ensure the parsed UUID is identical to the input
            return str(parsed_uuid).lower() == transaction_id
        except (ValueError, TypeError):
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