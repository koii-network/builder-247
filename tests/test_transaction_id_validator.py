import pytest
from src.transaction_id_validator import TransactionIDValidator

class TestTransactionIDValidator:
    def test_valid_transaction_ids(self):
        """Test that valid transaction IDs pass validation."""
        valid_ids = [
            "abc123def456",
            "TRANSACTION_ID_2023",
            "12345abcde67890"
        ]
        
        for tx_id in valid_ids:
            assert TransactionIDValidator.validate_transaction_id(tx_id) is True
    
    def test_invalid_transaction_ids(self):
        """Test that invalid transaction IDs fail validation."""
        invalid_ids = [
            "",  # Empty string
            None,  # None type
            "short",  # Too short
            "a" * 51,  # Too long
            "transaction id with spaces",  # Contains spaces
            "!@#$%^&*()",  # Special characters
        ]
        
        for tx_id in invalid_ids:
            assert TransactionIDValidator.validate_transaction_id(tx_id) is False
    
    def test_benchmark_validation(self):
        """Test the performance benchmarking method."""
        test_ids = [
            "abc123def456",
            "TRANSACTION_2023",
            "12345abcde67890"
        ]
        
        # Benchmark validation
        benchmark_results = TransactionIDValidator.benchmark_validation(test_ids)
        
        # Validate benchmark results
        assert 'mean_validation_time_ms' in benchmark_results
        assert 'median_validation_time_ms' in benchmark_results
        assert 'min_validation_time_ms' in benchmark_results
        assert 'max_validation_time_ms' in benchmark_results
        assert 'total_iterations' in benchmark_results
        assert 'validation_results' in benchmark_results
        
        # Validate results
        assert len(benchmark_results['validation_results']) == len(test_ids)
        assert all(isinstance(result, bool) for result in benchmark_results['validation_results'])
        
        # Performance checks
        assert benchmark_results['total_iterations'] == 1000
        assert benchmark_results['mean_validation_time_ms'] >= 0
        assert benchmark_results['max_validation_time_ms'] >= benchmark_results['min_validation_time_ms']
    
    def test_benchmark_large_dataset(self):
        """Test benchmarking with a larger dataset."""
        large_test_ids = [f"transaction_{i}" for i in range(100)]
        
        benchmark_results = TransactionIDValidator.benchmark_validation(large_test_ids, iterations=500)
        
        assert len(benchmark_results['validation_results']) == len(large_test_ids)
        assert benchmark_results['total_iterations'] == 500