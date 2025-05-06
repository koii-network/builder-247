import time
import uuid
from typing import Callable, List, Dict, Any
import statistics

class TransactionIDBenchmark:
    """
    Performance benchmarking utility for transaction ID validation.
    
    This class provides methods to measure the performance of transaction ID validation 
    with various metrics and strategies.
    """
    
    @staticmethod
    def generate_transaction_ids(count: int) -> List[str]:
        """
        Generate a specified number of unique transaction IDs.
        
        Args:
            count (int): Number of transaction IDs to generate
        
        Returns:
            List[str]: List of generated transaction IDs
        """
        return [str(uuid.uuid4()) for _ in range(count)]
    
    @staticmethod
    def validate_transaction_id(transaction_id: str) -> bool:
        """
        Basic transaction ID validation method.
        
        Args:
            transaction_id (str): Transaction ID to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check if it's a valid UUID
            uuid.UUID(transaction_id)
            return True
        except ValueError:
            return False
    
    def benchmark_validation(
        self, 
        validator: Callable[[str], bool], 
        transaction_ids: List[str], 
        iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Benchmark the performance of a transaction ID validation method.
        
        Args:
            validator (Callable): Function to validate transaction IDs
            transaction_ids (List[str]): List of transaction IDs to validate
            iterations (int, optional): Number of times to repeat the benchmark. Defaults to 10.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        if not transaction_ids:
            return {
                'total_ids': 0,
                'avg_validation_time': 0.0,
                'min_validation_time': 0.0,
                'max_validation_time': 0.0,
                'std_dev_validation_time': 0.0,
                'validation_rate': 0.0
            }
        
        validation_times = []
        validation_results = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            results = [validator(tid) for tid in transaction_ids]
            end_time = time.perf_counter()
            
            validation_times.append(end_time - start_time)
            validation_results.append(results)
        
        valid_count = sum(sum(results) for results in validation_results) / iterations
        total_ids = len(transaction_ids)
        
        return {
            'total_ids': total_ids,
            'avg_validation_time': statistics.mean(validation_times),
            'min_validation_time': min(validation_times),
            'max_validation_time': max(validation_times),
            'std_dev_validation_time': statistics.stdev(validation_times) if len(validation_times) > 1 else 0,
            'validation_rate': valid_count / total_ids
        }