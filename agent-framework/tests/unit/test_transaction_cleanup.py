import pytest
from prometheus_swarm.utils.transaction_cleanup import clean_transaction_id, cleanup_transaction_ids

def test_clean_transaction_id_basic():
    """Test basic transaction ID cleaning."""
    assert clean_transaction_id("ABC-123") == "abc123"
    assert clean_transaction_id("  Hello World! 123  ") == "helloworld123"
    assert clean_transaction_id(456) == "456"

def test_clean_transaction_id_edge_cases():
    """Test edge cases for transaction ID cleaning."""
    assert clean_transaction_id(None) is None
    assert clean_transaction_id("") is None
    assert clean_transaction_id("   ") is None
    assert clean_transaction_id("a" * 100) == "a" * 50

def test_clean_transaction_id_special_chars():
    """Test removal of special characters."""
    assert clean_transaction_id("tx_id-123!@#") == "txid123"
    assert clean_transaction_id("🚀 Transaction 🌟") == "transaction"

def test_cleanup_transaction_ids_single():
    """Test cleaning a single transaction ID."""
    assert cleanup_transaction_ids("ABC-123") == ["abc123"]
    assert cleanup_transaction_ids(456) == ["456"]

def test_cleanup_transaction_ids_multiple():
    """Test cleaning multiple transaction IDs."""
    input_ids = ["ABC-123", "  XYZ 456  ", "ABC-123", None, ""]
    expected = ["abc123", "xyz456"]
    assert cleanup_transaction_ids(input_ids) == expected

def test_cleanup_transaction_ids_duplicates():
    """Test removing duplicates while preserving order."""
    input_ids = ["first", "second", "first", "third", "second"]
    expected = ["first", "second", "third"]
    assert cleanup_transaction_ids(input_ids) == expected