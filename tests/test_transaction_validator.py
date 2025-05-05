import pytest
import uuid
from src.transaction_validator import TransactionIDValidator

class TestTransactionIDValidator:
    def test_validate_uuid_valid(self):
        """Test valid UUID v4 transaction ID"""
        valid_uuid = str(uuid.uuid4())
        assert TransactionIDValidator.validate_uuid(valid_uuid) is True
    
    def test_validate_uuid_invalid(self):
        """Test invalid UUID transaction ID"""
        invalid_uuids = [
            'not-a-uuid',
            str(uuid.uuid1()),  # v1 UUID
            '12345',
            ''
        ]
        for invalid_uuid in invalid_uuids:
            assert TransactionIDValidator.validate_uuid(invalid_uuid) is False
    
    def test_validate_custom_format(self):
        """Test custom format validation"""
        valid_formats = [
            'AB123456CD',  # default pattern
            'XY987654ZW'
        ]
        invalid_formats = [
            'ab123456cd',  # lowercase
            '123456',      # no letters
            'ABCDEFGHIJ'   # too many letters
        ]
        
        for valid_format in valid_formats:
            assert TransactionIDValidator.validate_custom_format(valid_format) is True
        
        for invalid_format in invalid_formats:
            assert TransactionIDValidator.validate_custom_format(invalid_format) is False
    
    def test_validate_custom_pattern(self):
        """Test custom regex pattern validation"""
        # Custom pattern: starts with 'TX', followed by 6 digits
        custom_pattern = r'^TX\d{6}$'
        
        valid_tx_ids = ['TX123456', 'TX987654']
        invalid_tx_ids = ['TX12345', 'TX1234567', 'AB123456']
        
        for valid_tx_id in valid_tx_ids:
            assert TransactionIDValidator.validate_custom_format(valid_tx_id, custom_pattern) is True
        
        for invalid_tx_id in invalid_tx_ids:
            assert TransactionIDValidator.validate_custom_format(invalid_tx_id, custom_pattern) is False
    
    def test_validate_length(self):
        """Test transaction ID length validation"""
        valid_lengths = [
            '1234567890',     # 10 chars
            'x' * 25,         # within range
            'x' * 50          # max length
        ]
        invalid_lengths = [
            '123',            # too short
            'x' * 51,         # too long
            ''                # empty string
        ]
        
        for valid_length in valid_lengths:
            assert TransactionIDValidator.validate_length(valid_length) is True
        
        for invalid_length in invalid_lengths:
            assert TransactionIDValidator.validate_length(invalid_length) is False
    
    def test_comprehensive_validate(self):
        """Test comprehensive validation method"""
        # Valid UUID
        valid_uuid = str(uuid.uuid4())
        assert TransactionIDValidator.validate(valid_uuid) is True
        
        # Custom pattern
        assert TransactionIDValidator.validate('AB123456CD') is False
        assert TransactionIDValidator.validate('AB123456CD', uuid_validation=False, 
                                               custom_pattern=r'^[A-Z]{2}\d{6}[A-Z]{2}$') is True
    
    def test_validate_type_error(self):
        """Test type validation"""
        with pytest.raises(TypeError):
            TransactionIDValidator.validate(123)
        with pytest.raises(TypeError):
            TransactionIDValidator.validate(None)
    
    def test_validate_with_custom_length(self):
        """Test validation with custom length constraints"""
        # Short transaction ID with custom length
        assert TransactionIDValidator.validate('TX123', 
                                               uuid_validation=False, 
                                               min_length=3, 
                                               max_length=5) is True
        
        # Too long transaction ID
        assert TransactionIDValidator.validate('VERY_LONG_TRANSACTION_ID', 
                                               uuid_validation=False, 
                                               max_length=10) is False