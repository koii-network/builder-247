import re
import time
from typing import Union, Dict, Any
import uuid

class TransactionIDValidator:
    @staticmethod
    def validate_transaction_id(transaction_id: str) -> bool:
        """
        Validate a transaction ID based on multiple criteria.
        
        Args:
            transaction_id (str): The transaction ID to validate
        
        Returns:
            bool: True if transaction ID is valid, False otherwise
        """
        # Check if transaction_id is None or empty
        if not transaction_id:
            return False
        
        # Check length (UUID is typically 36 characters)
        if len(transaction_id) != 36:
            return False
        
        # Use UUID validation
        try:
            uuid.UUID(transaction_id)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def benchmark_transaction_id_validation(iterations: int = 10000) -> Dict[str, Any]:
        """
        Benchmark transaction ID validation performance.
        
        Args:
            iterations (int): Number of validation iterations to run
        
        Returns:
            Dict containing performance metrics
        """
        valid_id = str(uuid.uuid4())
        invalid_id = "invalid-transaction-id"
        
        start_time = time.time()
        
        valid_count = 0
        invalid_count = 0
        
        for _ in range(iterations):
            if TransactionIDValidator.validate_transaction_id(valid_id):
                valid_count += 1
            if not TransactionIDValidator.validate_transaction_id(invalid_id):
                invalid_count += 1
        
        end_time = time.time()
        
        return {
            "total_iterations": iterations,
            "total_time_seconds": end_time - start_time,
            "avg_time_per_validation_microseconds": ((end_time - start_time) * 1_000_000) / (iterations * 2),
            "valid_validations": valid_count,
            "invalid_validations": invalid_count
        }