import pytest
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_ids():
    """Test valid transaction ID variations."""
    valid_ids = [
        'valid-transaction-123',
        'valid_transaction_456',
        'validTransaction789',
        'transaction-id-with-numbers-123',
        'a' * 50,  # Maximum length
        'tx-123-456-789',
    ]
    
    for transaction_id in valid_ids:
        assert validate_transaction_id(transaction_id) == True, f"Failed for {transaction_id}"

def test_invalid_transaction_ids():
    """Test invalid transaction ID variations."""
    invalid_ids = [
        None,                 # None
        '',                   # Empty string
        '   ',                # Whitespace
        'short',              # Too short
        'a' * 51,             # Too long
        '-invalid-start',     # Starts with hyphen
        'invalid-end-',       # Ends with hyphen
        '_invalid_start',     # Starts with underscore
        'invalid_end_',       # Ends with underscore
        'invalid characters!@#',  # Special characters
    ]
    
    for transaction_id in invalid_ids:
        assert validate_transaction_id(transaction_id) == False, f"Incorrectly validated {transaction_id}"

def test_input_types():
    """Test different input types."""
    non_string_inputs = [
        123,                  # Integer
        3.14,                 # Float
        [],                   # List
        {},                   # Dictionary
        True,                 # Boolean
    ]
    
    for input_val in non_string_inputs:
        assert validate_transaction_id(input_val) == False, f"Incorrectly validated {input_val}"