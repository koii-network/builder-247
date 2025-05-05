import pytest
import re
import uuid
from src.transaction_cleanup import clean_transaction_id

def test_clean_transaction_id_basic():
    """Test basic transaction ID cleaning"""
    assert clean_transaction_id("  Transaction123  ") == "transaction123"

def test_clean_transaction_id_special_chars():
    """Test removal of special characters"""
    assert clean_transaction_id("Trans@ction#123!") == "transaction123"

def test_clean_transaction_id_mixed_case():
    """Test conversion to lowercase"""
    assert clean_transaction_id("TransAction123") == "transaction123"

def test_clean_transaction_id_length_limit():
    """Test truncation to 50 characters"""
    long_id = "a" * 100
    assert len(clean_transaction_id(long_id)) == 50

def test_clean_transaction_id_empty_input():
    """Test empty input raises ValueError"""
    with pytest.raises(ValueError, match="Transaction ID cannot be empty"):
        clean_transaction_id("")

def test_clean_transaction_id_none_input():
    """Test None input raises ValueError"""
    with pytest.raises(ValueError, match="Transaction ID cannot be empty"):
        clean_transaction_id(None)

def test_clean_transaction_id_whitespace_only():
    """Test input with only whitespace generates a UUID"""
    result = clean_transaction_id("   \t\n")
    
    # Verify it looks like a valid UUID
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', result)

def test_clean_transaction_id_uuid_generation():
    """Test UUID generation for invalid inputs"""
    result1 = clean_transaction_id("!!!@@@")
    result2 = clean_transaction_id("!!!@@@")
    
    # Verify it generates valid UUIDs
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', result1)
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', result2)
    
    # Ensure different invalid inputs generate different UUIDs
    assert result1 != result2

def test_clean_transaction_id_with_hyphens():
    """Test that hyphens are preserved"""
    assert clean_transaction_id("transaction-123-abc") == "transaction-123-abc"