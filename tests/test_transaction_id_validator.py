import pytest
import uuid
from src.transaction_id_validator import TransactionIDValidator

class TestTransactionIDValidator:
    def test_valid_uuid_transaction_id(self):
        """Test that a valid UUID is recognized as a valid transaction ID."""
        valid_id = str(uuid.uuid4())
        assert TransactionIDValidator.validate_transaction_id(valid_id) is True

    def test_invalid_transaction_ids(self):
        """Test various invalid transaction ID scenarios."""
        invalid_cases = [
            None,           # None value
            "",             # Empty string
            "invalid-uuid", # Malformed UUID
            12345,          # Integer
            "  ",           # Whitespace
        ]
        
        for invalid_id in invalid_cases:
            assert TransactionIDValidator.validate_transaction_id(invalid_id) is False

    def test_generate_test_transaction_ids(self):
        """Test the generation of test transaction IDs."""
        num_ids = 50
        ids = TransactionIDValidator.generate_test_transaction_ids(num_ids)
        
        assert len(ids) == num_ids
        
        # Verify each generated ID is a valid UUID
        for id_str in ids:
            assert TransactionIDValidator.validate_transaction_id(id_str) is True

    def test_benchmark_validation(self):
        """Test the benchmarking method for transaction ID validation."""
        # Generate test transaction IDs
        test_ids = TransactionIDValidator.generate_test_transaction_ids(100)
        
        # Run benchmark
        min_time, max_time, avg_time = TransactionIDValidator.benchmark_validation(
            TransactionIDValidator.validate_transaction_id, 
            test_ids
        )
        
        # Verify benchmark results
        assert min_time >= 0
        assert max_time >= min_time
        assert avg_time >= 0

    def test_benchmark_empty_list_raises_error(self):
        """Test that benchmarking with an empty list raises a ValueError."""
        with pytest.raises(ValueError, match="Transaction IDs list cannot be empty"):
            TransactionIDValidator.benchmark_validation(
                TransactionIDValidator.validate_transaction_id, 
                []
            )

    def test_benchmark_different_iterations(self):
        """Test benchmarking with different numbers of iterations."""
        test_ids = TransactionIDValidator.generate_test_transaction_ids(50)
        
        # Test with default and custom iteration counts
        for num_iterations in [10, 100, 1000]:
            min_time, max_time, avg_time = TransactionIDValidator.benchmark_validation(
                TransactionIDValidator.validate_transaction_id, 
                test_ids, 
                num_iterations=num_iterations
            )
            
            assert min_time >= 0
            assert max_time >= min_time
            assert avg_time >= 0