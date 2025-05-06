import pytest
import uuid
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_id():
    """Test that a valid UUID v4 is recognized as valid."""
    valid_id = str(uuid.uuid4())
    assert validate_transaction_id(valid_id) is True

def test_invalid_uuid_format():
    """Test that incorrectly formatted UUIDs are rejected."""
    # UUID v1 format
    invalid_id = str(uuid.uuid1())
    assert validate_transaction_id(invalid_id) is False

def test_malformed_uuid():
    """Test various malformed UUID formats."""
    test_cases = [
        # Partially correct UUID
        "550e8400-e29b-41d4-a716-446655440000extra",
        # Incorrect separators 
        "550e8400_e29b_41d4_a716_446655440000",
        # Incorrect length 
        "550e8400-e29b-41d4-a716-44665544",
        # Random string
        "not-a-uuid-at-all"
    ]
    
    for case in test_cases:
        assert validate_transaction_id(case) is False

def test_edge_cases():
    """Test various edge cases for transaction ID validation."""
    test_cases = [
        # Empty string
        "",
        # Whitespace string
        "   ",
        # None
        None,
        # Integer
        123,
        # Float
        3.14,
        # List
        [str(uuid.uuid4())],
        # Tuple of UUID
        (str(uuid.uuid4()),)
    ]
    
    for case in test_cases:
        assert validate_transaction_id(case) is False

def test_case_sensitive_uuid():
    """Ensure UUID validation is case-sensitive."""
    valid_id = str(uuid.uuid4())
    lowercase_id = valid_id.lower()
    uppercase_id = valid_id.upper()
    
    # The original case of the UUID matters
    if valid_id == lowercase_id:
        assert validate_transaction_id(uppercase_id) is False
    else:
        assert validate_transaction_id(lowercase_id) is False