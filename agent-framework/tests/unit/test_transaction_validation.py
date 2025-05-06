import pytest
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_ids():
    """Test valid transaction ID formats."""
    valid_ids = [
        'abc12345',           # Minimum length, mixed alphanumeric
        'validTransactionId', # Longer alphanumeric
        '12345678',           # All numeric
        'ABCDEFGH',           # All uppercase
        '1234567890abcdef'    # Mix of numbers and letters
    ]
    
    for valid_id in valid_ids:
        assert validate_transaction_id(valid_id) is True, f"Failed for valid ID: {valid_id}"

def test_invalid_transaction_ids():
    """Test invalid transaction ID formats."""
    invalid_ids = [
        None,                 # None value
        '',                   # Empty string
        '   ',                # Whitespace
        'short',              # Too short (< 8 chars)
        'a' * 65,             # Too long (> 64 chars)
        'invalid-id',         # Contains special characters
        'invalid id',         # Contains spaces
        '!@#$%^&*',           # Special characters only
        None,                 # None 
        123,                  # Numeric value 
        1234567               # Too short numeric value
    ]
    
    for invalid_id in invalid_ids:
        assert validate_transaction_id(invalid_id) is False, f"Failed for invalid ID: {invalid_id}"

def test_edge_cases():
    """Test edge case scenarios."""
    # Test minimum and maximum valid lengths
    assert validate_transaction_id('a' * 8) is True
    assert validate_transaction_id('a' * 64) is True
    
    # Test just outside valid length
    assert validate_transaction_id('a' * 7) is False
    assert validate_transaction_id('a' * 65) is False
    
    # Test type conversion
    assert validate_transaction_id(12345678) is True
    assert validate_transaction_id(1234) is False