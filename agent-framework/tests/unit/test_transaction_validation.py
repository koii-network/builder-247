import pytest
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_ids():
    """Test various valid transaction ID formats."""
    valid_ids = [
        # UUID format
        str(pytest.helpers.random_uuid()),
        
        # Alphanumeric with special characters
        'transaction_123-xyz.456',
        'ABCDEF1234_transaction',
        'unique_transaction_id_2023',
        
        # Boundary conditions
        'a' * 10,  # Minimum length
        'a' * 50,  # Maximum length
    ]
    
    for transaction_id in valid_ids:
        assert validate_transaction_id(transaction_id), f"Failed for valid ID: {transaction_id}"

def test_invalid_transaction_ids():
    """Test various invalid transaction ID formats."""
    invalid_ids = [
        # Too short
        'a' * 9,
        
        # Too long
        'a' * 51,
        
        # Non-string inputs
        None,
        123,
        [],
        {},
        
        # Special characters not allowed
        'transaction@invalid',
        'transaction#invalid',
        'transaction$invalid',
        
        # Empty string
        '',
        
        # Whitespace
        ' transaction ',
        'transaction id'
    ]
    
    for transaction_id in invalid_ids:
        assert not validate_transaction_id(transaction_id), f"Failed to reject invalid ID: {transaction_id}"

def test_edge_cases():
    """Test edge cases for transaction ID validation."""
    # Unicode characters not allowed
    assert not validate_transaction_id('transaction_🚀'), "Unicode characters should not be allowed"
    
    # Case sensitivity check
    assert validate_transaction_id('UPPERCASE_transaction'), "Uppercase letters should be allowed"
    assert validate_transaction_id('lowercase_transaction'), "Lowercase letters should be allowed"
    
    # Mixed case and alphanumeric
    assert validate_transaction_id('MixedCase123_Transaction'), "Mixed case alphanumeric should be valid"