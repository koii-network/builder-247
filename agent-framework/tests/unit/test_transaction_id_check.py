"""
Unit tests for the TransactionIDDuplicateChecker.
"""
import pytest
from prometheus_swarm.utils.transaction_id_check import TransactionIDDuplicateChecker


def test_transaction_id_duplicate_checker_basic():
    """
    Test basic functionality of duplicate checking.
    """
    checker = TransactionIDDuplicateChecker()
    
    # First time should return False (not a duplicate)
    assert not checker.is_duplicate("tx1")
    
    # Second time should return True (now it's a duplicate)
    assert checker.is_duplicate("tx1")


def test_transaction_id_duplicate_checker_multiple_ids():
    """
    Test checking multiple unique and duplicate transaction IDs.
    """
    checker = TransactionIDDuplicateChecker()
    
    # Check multiple unique IDs
    assert not checker.is_duplicate("tx1")
    assert not checker.is_duplicate("tx2")
    assert not checker.is_duplicate("tx3")
    
    # Now check duplicates
    assert checker.is_duplicate("tx1")
    assert checker.is_duplicate("tx2")
    assert checker.is_duplicate("tx3")


def test_transaction_id_duplicate_checker_max_stored_ids():
    """
    Test that only the most recent IDs are stored.
    """
    checker = TransactionIDDuplicateChecker(max_stored_ids=3)
    
    # Add more than max stored IDs
    assert not checker.is_duplicate("tx1")
    assert not checker.is_duplicate("tx2")
    assert not checker.is_duplicate("tx3")
    assert not checker.is_duplicate("tx4")
    
    # Check stored IDs
    assert checker.get_stored_ids() == ["tx2", "tx3", "tx4"]
    
    # Check duplicates
    assert checker.is_duplicate("tx3")
    assert checker.is_duplicate("tx4")


def test_transaction_id_duplicate_checker_clear():
    """
    Test clearing stored transaction IDs.
    """
    checker = TransactionIDDuplicateChecker()
    
    assert not checker.is_duplicate("tx1")
    assert checker.is_duplicate("tx1")
    
    # Clear and check again
    checker.clear()
    assert not checker.is_duplicate("tx1")


def test_transaction_id_duplicate_checker_empty_id_error():
    """
    Test handling of empty transaction ID.
    """
    checker = TransactionIDDuplicateChecker()
    
    with pytest.raises(ValueError, match="Transaction ID cannot be empty or None"):
        checker.is_duplicate("")
    
    with pytest.raises(ValueError, match="Transaction ID cannot be empty or None"):
        checker.is_duplicate(None)  # type: ignore