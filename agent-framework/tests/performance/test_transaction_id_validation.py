import pytest
import uuid
from prometheus_swarm.performance.transaction_id_validation import TransactionIDBenchmark

class TestTransactionIDBenchmark:
    
    def setup_method(self):
        self.benchmark = TransactionIDBenchmark()
    
    def test_generate_transaction_ids(self):
        """Test that unique transaction IDs are generated."""
        ids = self.benchmark.generate_transaction_ids(100)
        assert len(ids) == 100
        assert len(set(ids)) == 100  # All unique
    
    def test_validate_transaction_id(self):
        """Test transaction ID validation logic."""
        valid_uuid = str(uuid.uuid4())
        invalid_uuid = "not-a-uuid"
        
        assert self.benchmark.validate_transaction_id(valid_uuid) is True
        assert self.benchmark.validate_transaction_id(invalid_uuid) is False
    
    def test_benchmark_validation(self):
        """Test the benchmark method with various scenarios."""
        transaction_ids = self.benchmark.generate_transaction_ids(50)
        
        # Validate with the default validator
        results = self.benchmark.benchmark_validation(
            validator=self.benchmark.validate_transaction_id, 
            transaction_ids=transaction_ids,
            iterations=5
        )
        
        # Assert structure of results
        expected_keys = [
            'total_ids', 'avg_validation_time', 
            'min_validation_time', 'max_validation_time', 
            'std_dev_validation_time', 'validation_rate'
        ]
        for key in expected_keys:
            assert key in results
        
        # Numeric assertions
        assert results['total_ids'] == 50
        assert results['validation_rate'] >= 0.9  # Most should be valid
        assert results['avg_validation_time'] > 0
        assert results['avg_validation_time'] < 1.0  # Validation should be quick
    
    def test_benchmark_custom_validator(self):
        """Test benchmarking with a custom validator."""
        def strict_validator(tid: str) -> bool:
            """A custom validator that is more restrictive."""
            return len(tid) > 10 and self.benchmark.validate_transaction_id(tid)
        
        transaction_ids = self.benchmark.generate_transaction_ids(20)
        results = self.benchmark.benchmark_validation(
            validator=strict_validator, 
            transaction_ids=transaction_ids,
            iterations=3
        )
        
        assert 'validation_rate' in results
    
    def test_edge_cases(self):
        """Test edge cases in transaction ID generation and validation."""
        # Empty list
        results = self.benchmark.benchmark_validation(
            validator=self.benchmark.validate_transaction_id, 
            transaction_ids=[],
            iterations=1
        )
        assert results['total_ids'] == 0
        assert results['validation_rate'] == 0
        
        # Very large number of IDs
        large_ids = self.benchmark.generate_transaction_ids(1000)
        results = self.benchmark.benchmark_validation(
            validator=self.benchmark.validate_transaction_id, 
            transaction_ids=large_ids,
            iterations=2
        )
        assert results['total_ids'] == 1000