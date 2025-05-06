import re
import time
import statistics
from typing import List, Dict, Any, Optional

class TransactionIDValidator:
    """
    A performance-optimized transaction ID validation utility.
    
    This class provides methods to validate transaction IDs and benchmark their performance.
    """
    
    @staticmethod
    def validate_transaction_id(transaction_id: str) -> bool:
        """
        Validate a transaction ID based on standard criteria.
        
        Args:
            transaction_id (str): The transaction ID to validate.
        
        Returns:
            bool: True if the transaction ID is valid, False otherwise.
        """
        # Check if transaction_id is a non-empty string
        if not isinstance(transaction_id, str) or not transaction_id:
            return False
        
        # Optional: Add specific validation rules (e.g., format, length)
        # Example: Alphanumeric ID between 10-50 characters
        return bool(re.match(r'^[a-zA-Z0-9]{10,50}$', transaction_id))
    
    @staticmethod
    def benchmark_validation(transaction_ids: List[str], iterations: int = 1000) -> Dict[str, Any]:
        """
        Benchmark the performance of transaction ID validation.
        
        Args:
            transaction_ids (List[str]): List of transaction IDs to benchmark.
            iterations (int, optional): Number of times to run the validation. Defaults to 1000.
        
        Returns:
            Dict[str, Any]: Performance metrics for the validation process.
        """
        validation_times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            
            # Validate each transaction ID
            results = [TransactionIDValidator.validate_transaction_id(txn_id) for txn_id in transaction_ids]
            
            end_time = time.perf_counter()
            validation_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        return {
            "mean_validation_time_ms": statistics.mean(validation_times),
            "median_validation_time_ms": statistics.median(validation_times),
            "min_validation_time_ms": min(validation_times),
            "max_validation_time_ms": max(validation_times),
            "total_iterations": iterations,
            "validation_results": results
        }