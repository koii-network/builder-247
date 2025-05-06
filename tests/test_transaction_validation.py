import pytest
import uuid
from src.transaction_validation import TransactionIDValidator

class TestTransactionIDValidator:
    def test_valid_uuid_transaction_id(self):
        valid_id = str(uuid.uuid4())
        assert TransactionIDValidator.validate_transaction_id(valid_id) is True
    
    def test_invalid_transaction_ids(self):
        test_cases = [
            None,  # None
            "",    # Empty string
            "short",  # Too short
            "123456789012345678901234567890123456",  # Wrong format
            "not-a-valid-uuid",  # Invalid UUID string
            "z" * 36  # Invalid characters
        ]
        
        for invalid_id in test_cases:
            assert TransactionIDValidator.validate_transaction_id(invalid_id) is False
    
    def test_benchmark_performance(self):
        benchmark_results = TransactionIDValidator.benchmark_transaction_id_validation()
        
        assert 'total_iterations' in benchmark_results
        assert 'total_time_seconds' in benchmark_results
        assert 'avg_time_per_validation_microseconds' in benchmark_results
        assert 'valid_validations' in benchmark_results
        assert 'invalid_validations' in benchmark_results
        
        # Performance sanity checks
        assert benchmark_results['total_iterations'] == 10000
        assert benchmark_results['total_time_seconds'] > 0
        assert benchmark_results['avg_time_per_validation_microseconds'] > 0
        assert benchmark_results['valid_validations'] > 0
        assert benchmark_results['invalid_validations'] > 0
    
    def test_edge_case_performance(self):
        # Test with different batch sizes
        for iterations in [100, 1000, 10000, 100000]:
            benchmark_results = TransactionIDValidator.benchmark_transaction_id_validation(iterations)
            assert benchmark_results['total_iterations'] == iterations