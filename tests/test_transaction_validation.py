import pytest
import uuid
from src.transaction_validation import validate_transaction_id

def test_valid_transaction_id():
    """Test that valid UUIDs pass validation."""
    valid_id = str(uuid.uuid4())
    assert validate_transaction_id(valid_id) is True

def test_invalid_transaction_ids():
    """Test various invalid transaction ID scenarios."""
    # Empty string
    assert validate_transaction_id('') is False
    
    # None input
    assert validate_transaction_id(None) is False
    
    # Too long
    long_id = str(uuid.uuid4()) + 'extra'
    assert validate_transaction_id(long_id) is False
    
    # Invalid UUID version (not v4)
    invalid_version = 'f47ac10b-58cc-3372-a567-0e02b2c3d479'
    assert validate_transaction_id(invalid_version) is False

def test_uuid_variations():
    """Test different UUID case and format variations."""
    # Lowercase
    lowercase_uuid = str(uuid.uuid4()).lower()
    assert validate_transaction_id(lowercase_uuid) is True
    
    # Uppercase 
    uppercase_uuid = str(uuid.uuid4()).upper()
    assert validate_transaction_id(uppercase_uuid) is True

def test_edge_cases():
    """Test edge case inputs for transaction ID validation."""
    # Random string
    assert validate_transaction_id('not-a-uuid') is False
    
    # Partial UUID
    assert validate_transaction_id('f47ac10b-58cc-4372') is False
    
    # Special characters
    assert validate_transaction_id('f47ac10b-58cc-4372-a567-0e02b2c3d4!9') is False

def test_uuid_generation_and_validation():
    """Ensure multiple generated UUIDs pass validation."""
    for _ in range(100):
        test_id = str(uuid.uuid4())
        assert validate_transaction_id(test_id) is True