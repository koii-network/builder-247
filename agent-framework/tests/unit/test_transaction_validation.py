import pytest
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_ids():
    """Test valid transaction ID scenarios."""
    assert validate_transaction_id("valid123transaction") == "valid123transaction"
    assert validate_transaction_id("a" * 10) == "a" * 10
    assert validate_transaction_id("z" * 100) == "z" * 100
    assert validate_transaction_id(12345678901) == "12345678901"

def test_invalid_transaction_ids():
    """Test invalid transaction ID scenarios."""
    # None input
    assert validate_transaction_id(None) is None
    
    # Too short
    assert validate_transaction_id("short") is None
    
    # Too long
    assert validate_transaction_id("a" * 101) is None
    
    # Non-alphanumeric characters
    assert validate_transaction_id("invalid-transaction") is None
    assert validate_transaction_id("invalid transaction") is None
    assert validate_transaction_id("transaction@123") is None

def test_type_error():
    """Test that TypeError is raised for unsupported types."""
    with pytest.raises(TypeError):
        validate_transaction_id(3.14)
    
    with pytest.raises(TypeError):
        validate_transaction_id([])
    
    with pytest.raises(TypeError):
        validate_transaction_id({})

def test_whitespace_handling():
    """Test handling of whitespace in transaction IDs."""
    assert validate_transaction_id("  valid123transaction  ") == "valid123transaction"
    assert validate_transaction_id(" ") is None