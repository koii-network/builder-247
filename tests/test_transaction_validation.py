import pytest
import uuid
from src.transaction_validation import validate_transaction_id

def test_valid_transaction_id():
    """Test a valid transaction ID (standard UUID v4)"""
    valid_id = str(uuid.uuid4())
    assert validate_transaction_id(valid_id) is True

def test_invalid_transaction_id_types():
    """Test invalid input types"""
    assert validate_transaction_id(None) is False
    assert validate_transaction_id(123) is False
    assert validate_transaction_id([]) is False
    assert validate_transaction_id({}) is False

def test_empty_transaction_id():
    """Test empty transaction ID"""
    assert validate_transaction_id("") is False

def test_incorrect_length_transaction_id():
    """Test transaction IDs with incorrect lengths"""
    # Shorter than UUID length
    assert validate_transaction_id("short") is False
    
    # Longer than UUID length
    long_id = str(uuid.uuid4()) + "extra"
    assert validate_transaction_id(long_id) is False

def test_whitespace_transaction_id():
    """Test transaction IDs with whitespace"""
    valid_id = str(uuid.uuid4())
    
    # Whitespace at the beginning
    assert validate_transaction_id(f" {valid_id}") is False
    
    # Whitespace at the end
    assert validate_transaction_id(f"{valid_id} ") is False
    
    # Whitespace in the middle
    assert validate_transaction_id(f"{valid_id[:18]} {valid_id[18:]}") is False

def test_invalid_uuid_format():
    """Test invalid UUID formats"""
    # Invalid UUID patterns
    invalid_ids = [
        "not-a-valid-uuid",
        "12345678-1234-1234-1234-123456789012",  # Looks like a UUID but invalid
        "00000000-0000-0000-0000-000000000000",  # Technically valid UUID but not v4
    ]
    
    for invalid_id in invalid_ids:
        assert validate_transaction_id(invalid_id) is False