import pytest
import uuid
from src.transaction_id_validator import TransactionIDValidator

class TestTransactionIDValidator:
    def test_valid_uuid_transaction_id(self):
        """Test valid UUID transaction ID."""
        valid_id = str(uuid.uuid4())
        assert TransactionIDValidator.validate_transaction_id(valid_id) is True
    
    def test_invalid_transaction_id_formats(self):
        """Test various invalid transaction ID formats."""
        invalid_cases = [
            None,
            '',
            'not-a-uuid',
            '123',
            '12345678-abcd-1234-5678-1234567890ab-extra',  # too long
            '12345678abcd1234567812345678901x',  # invalid characters
            '12345678-abcd-1234-5678-1234567890ab',  # looks like UUID but isn't valid
            123456,  # integer
            {},  # dictionary
            []   # list
        ]
        
        for case in invalid_cases:
            assert TransactionIDValidator.validate_transaction_id(case) is False
    
    def test_benchmark_validation(self):
        """Test the benchmarking method with various scenarios."""
        # Generate test cases
        valid_uuids = [str(uuid.uuid4()) for _ in range(100)]
        invalid_uuids = ['invalid_id'] * 50
        mixed_cases = valid_uuids + invalid_uuids
        
        # Run benchmark
        benchmark_result = TransactionIDValidator.benchmark_validation(
            TransactionIDValidator.validate_transaction_id, 
            mixed_cases
        )
        
        # Verify benchmark results
        assert 'mean_time_ms' in benchmark_result
        assert 'median_time_ms' in benchmark_result
        assert 'min_time_ms' in benchmark_result
        assert 'max_time_ms' in benchmark_result
        assert 'std_dev_ms' in benchmark_result
        assert 'total_test_cases' in benchmark_result
        assert 'valid_cases' in benchmark_result
        
        # Check reasonable values
        assert benchmark_result['total_test_cases'] == 150
        assert benchmark_result['valid_cases'] == 100
        assert benchmark_result['mean_time_ms'] >= 0
        assert benchmark_result['median_time_ms'] >= 0
    
    def test_benchmark_edge_cases(self):
        """Test benchmarking with edge cases."""
        edge_cases = [
            None,
            str(uuid.uuid4()),
            'invalid_id',
            '',
            str(uuid.uuid4()) * 10
        ]
        
        # Run benchmark with edge cases
        benchmark_result = TransactionIDValidator.benchmark_validation(
            TransactionIDValidator.validate_transaction_id, 
            edge_cases
        )
        
        # Verify benchmark result keys
        expected_keys = [
            'mean_time_ms', 'median_time_ms', 
            'min_time_ms', 'max_time_ms', 
            'std_dev_ms', 'total_test_cases', 
            'valid_cases'
        ]
        
        for key in expected_keys:
            assert key in benchmark_result
    
    def test_custom_iteration_count(self):
        """Test benchmark with custom iteration count."""
        test_cases = [str(uuid.uuid4()) for _ in range(10)]
        
        # Benchmark with custom iteration count
        benchmark_result = TransactionIDValidator.benchmark_validation(
            TransactionIDValidator.validate_transaction_id, 
            test_cases, 
            num_iterations=500
        )
        
        assert benchmark_result['total_test_cases'] == 10
        assert benchmark_result['valid_cases'] == 10