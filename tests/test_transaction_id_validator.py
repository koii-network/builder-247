import pytest
import uuid
from src.transaction_id_validator import TransactionIDValidator

class TestTransactionIDValidator:
    def setup_method(self):
        """Set up a new TransactionIDValidator for each test"""
        self.validator = TransactionIDValidator()
    
    def test_generate_transaction_id(self):
        """Test transaction ID generation"""
        transaction_id = self.validator.generate_transaction_id()
        
        # Check that generated ID is a valid string representation of UUID
        assert isinstance(transaction_id, str)
        assert len(transaction_id) > 0
        
        # Verify it's a valid UUID
        try:
            uuid.UUID(transaction_id)
        except ValueError:
            pytest.fail("Generated transaction ID is not a valid UUID")
    
    def test_validate_transaction_id_valid(self):
        """Test validation of valid transaction IDs"""
        # Generate a valid transaction ID
        valid_id = self.validator.generate_transaction_id()
        
        # Validate the ID
        assert self.validator.validate_transaction_id(valid_id) is True
    
    def test_validate_transaction_id_invalid(self):
        """Test validation of invalid transaction IDs"""
        # Test various invalid transaction IDs
        invalid_ids = [
            'invalid_id', 
            '123', 
            '', 
            None, 
            '550e8400-e29b-41d4-a716-446655440000x'  # extra character
        ]
        
        for invalid_id in invalid_ids:
            assert self.validator.validate_transaction_id(invalid_id) is False
    
    def test_benchmark_transaction_id_generation(self):
        """Test transaction ID generation benchmark"""
        benchmark_result = self.validator.benchmark_transaction_id_generation(iterations=100)
        
        # Verify the benchmark result structure
        assert 'min_time' in benchmark_result
        assert 'max_time' in benchmark_result
        assert 'mean_time' in benchmark_result
        assert 'median_time' in benchmark_result
        assert 'iterations' in benchmark_result
        
        # Check that times are valid (positive floats)
        assert benchmark_result['min_time'] >= 0
        assert benchmark_result['max_time'] >= 0
        assert benchmark_result['mean_time'] >= 0
        assert benchmark_result['median_time'] >= 0
        
        # Verify iterations
        assert benchmark_result['iterations'] == 100
    
    def test_benchmark_transaction_id_validation(self):
        """Test transaction ID validation benchmark"""
        benchmark_result = self.validator.benchmark_transaction_id_validation(iterations=100)
        
        # Verify the benchmark result structure
        assert 'min_time' in benchmark_result
        assert 'max_time' in benchmark_result
        assert 'mean_time' in benchmark_result
        assert 'median_time' in benchmark_result
        assert 'iterations' in benchmark_result
        
        # Check that times are valid (positive floats)
        assert benchmark_result['min_time'] >= 0
        assert benchmark_result['max_time'] >= 0
        assert benchmark_result['mean_time'] >= 0
        assert benchmark_result['median_time'] >= 0
        
        # Verify iterations (original + invalid)
        assert benchmark_result['iterations'] == 100 * 2