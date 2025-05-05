import pytest
from src.transaction_id_manager import TransactionIDManager

def test_generate_transaction_id():
    """Test transaction ID generation."""
    transaction_id1 = TransactionIDManager.generate_transaction_id()
    transaction_id2 = TransactionIDManager.generate_transaction_id()
    
    assert transaction_id1 is not None
    assert transaction_id2 is not None
    assert transaction_id1 != transaction_id2
    
    # Verify it looks like a valid UUID
    assert len(transaction_id1) == 36

def test_sanitize_transaction_id():
    """Test transaction ID sanitization."""
    test_cases = [
        # Normal cases
        ("valid-transaction-id", "validtransactionid"),
        ("  whitespace  ", "whitespace"),
        
        # Special character handling
        ("id@123!", "id123"),
        ("id_with_underscore", "idwithunderscore"),
        
        # Integer handling
        (12345, "12345"),
        
        # Edge cases
        (None, None),
        ("", None),
        ("   ", None)
    ]
    
    for input_id, expected in test_cases:
        result = TransactionIDManager.sanitize_transaction_id(input_id)
        assert result == expected

def test_long_transaction_id_truncation():
    """Test that long transaction IDs get truncated."""
    long_id = "a" * 200
    sanitized_id = TransactionIDManager.sanitize_transaction_id(long_id)
    
    assert sanitized_id is not None
    assert len(sanitized_id) <= 100

def test_is_valid_transaction_id():
    """Test transaction ID validation."""
    valid_test_cases = [
        "validid",
        "123456",
        "a" * 50,
        "mixedcase123"
    ]
    
    invalid_test_cases = [
        None,
        "",
        "   ",
        "a" * 101,
        "id with spaces",
        "special@chars!"
    ]
    
    for valid_id in valid_test_cases:
        assert TransactionIDManager.is_valid_transaction_id(valid_id), f"{valid_id} should be valid"
    
    for invalid_id in invalid_test_cases:
        assert not TransactionIDManager.is_valid_transaction_id(invalid_id), f"{invalid_id} should be invalid"