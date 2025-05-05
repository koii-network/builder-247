import pytest
import uuid
from src.transaction_validation import validate_transaction_id

def test_valid_transaction_id():
    """Test that a valid UUID v4 transaction ID returns True"""
    valid_id = str(uuid.uuid4())
    assert validate_transaction_id(valid_id) is True

def test_invalid_transaction_id_types():
    """Test various invalid input types"""
    invalid_inputs = [
        None,  # None
        "",    # Empty string
        "   ", # Whitespace string
        123,   # Integer
        3.14,  # Float
        [],    # List
        {},    # Dictionary
    ]
    
    for invalid_input in invalid_inputs:
        assert validate_transaction_id(invalid_input) is False

def test_invalid_uuid_formats():
    """Test invalid UUID formats"""
    invalid_uuids = [
        "not-a-uuid",  # Not a UUID
        "123e4567-e89b-12d3-a456-426614174000",  # Different UUID version
        str(uuid.uuid1()),  # UUID v1 (timestamp-based)
        str(uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org')),  # UUID v3 (namespace)
        str(uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')),  # UUID v5 (namespace)
        "123e4567-e89b-12d3-a456-42661417400",  # Too short
        "123e4567-e89b-12d3-a456-426614174000extra"  # Extra characters
    ]
    
    for invalid_uuid in invalid_uuids:
        assert validate_transaction_id(invalid_uuid) is False

def test_leading_trailing_whitespace():
    """Test that leading and trailing whitespace is handled correctly"""
    valid_id = str(uuid.uuid4())
    assert validate_transaction_id(f"  {valid_id}  ") is True

def test_edge_cases():
    """Test some edge cases for transaction ID validation"""
    # UUID with different separators and case
    test_cases = [
        uuid.uuid4(),
        str(uuid.uuid4()).upper(),
        str(uuid.uuid4()).replace('-', ''),
    ]
    
    for case in test_cases:
        assert validate_transaction_id(str(case)) is True