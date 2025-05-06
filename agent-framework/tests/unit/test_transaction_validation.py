import pytest
import uuid
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_uuid_transaction_id():
    """Test valid standard UUID transaction ID."""
    transaction_id = str(uuid.uuid4())
    assert validate_transaction_id(transaction_id) is True

def test_empty_transaction_id():
    """Test empty transaction ID."""
    assert validate_transaction_id('') is False
    assert validate_transaction_id('   ') is False

def test_whitespace_transaction_id():
    """Test transaction ID with only whitespace."""
    assert validate_transaction_id(' \t\n') is False

def test_non_string_transaction_id():
    """Test non-string transaction ID."""
    assert validate_transaction_id(123) is False
    assert validate_transaction_id(None) is False
    assert validate_transaction_id([]) is False

def test_transaction_id_max_length():
    """Test transaction ID length validation."""
    valid_max_length_id = str(uuid.uuid4())
    assert len(valid_max_length_id) <= 50
    assert validate_transaction_id(valid_max_length_id) is True

    # Create an ID longer than 50 characters
    long_id = str(uuid.uuid4()) * 2
    assert validate_transaction_id(long_id) is False

def test_invalid_uuid_format():
    """Test invalid UUID format."""
    invalid_formats = [
        'not-a-uuid',
        '12345',
        'abc-123-def',
        '00000000-0000-0000-0000-00000000000'  # Incomplete UUID
    ]
    
    for invalid_id in invalid_formats:
        assert validate_transaction_id(invalid_id) is False

def test_edge_cases():
    """Test various edge cases for transaction ID."""
    test_cases = [
        '',             # Empty string
        '   ',          # Whitespace
        str(uuid.uuid4()),  # Standard UUID
        '550e8400-e29b-41d4-a716-446655440000',  # Another valid UUID
        'x' * 51        # Exceeds max length
    ]
    
    expected_results = [
        False,          # Empty string
        False,          # Whitespace
        True,           # Standard UUID
        True,           # Another valid UUID
        False           # Exceeds max length
    ]
    
    for test_id, expected in zip(test_cases, expected_results):
        assert validate_transaction_id(test_id) is expected