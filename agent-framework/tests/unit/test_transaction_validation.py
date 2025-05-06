import pytest
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_ids():
    """Test various valid transaction ID scenarios."""
    assert validate_transaction_id("abc123") == True
    assert validate_transaction_id("TransactionID") == True
    assert validate_transaction_id(12345) == True
    assert validate_transaction_id("1") == True
    assert validate_transaction_id("a" * 50) == True  # Max length

def test_invalid_transaction_ids():
    """Test invalid transaction ID scenarios."""
    # None
    assert validate_transaction_id(None) == False

    # Empty string
    assert validate_transaction_id("") == False

    # Too long
    assert validate_transaction_id("a" * 51) == False

    # Non-alphanumeric string
    assert validate_transaction_id("transaction-id") == False
    assert validate_transaction_id("transaction_id") == False
    assert validate_transaction_id("transaction id") == False
    assert validate_transaction_id("!@#$%^&*") == False

    # Negative numbers
    assert validate_transaction_id(-123) == False
    assert validate_transaction_id(0) == False

def test_edge_cases():
    """Test edge case scenarios for transaction ID validation."""
    # Special characters and whitespace
    assert validate_transaction_id(" ") == False
    assert validate_transaction_id("\t") == False
    assert validate_transaction_id("\n") == False

    # Various data types
    assert validate_transaction_id(3.14) == False
    assert validate_transaction_id([]) == False
    assert validate_transaction_id({}) == False
    assert validate_transaction_id(True) == False
    assert validate_transaction_id(False) == False