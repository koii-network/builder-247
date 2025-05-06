"""
Unit tests for the TransactionTracker class.
"""
import pytest
from prometheus_swarm.utils.transaction_id import TransactionTracker


def test_transaction_tracker_initialization():
    """Test that TransactionTracker initializes correctly."""
    tracker = TransactionTracker()
    assert len(tracker._processed_transactions) == 0


def test_transaction_id_first_occurrence():
    """Test that first occurrence of a transaction ID returns False."""
    tracker = TransactionTracker()
    assert not tracker.is_duplicate("unique_transaction_1")


def test_transaction_id_duplicate():
    """Test that duplicate transaction IDs return True."""
    tracker = TransactionTracker()
    transaction_id = "duplicate_transaction"
    
    # First occurrence should return False
    assert not tracker.is_duplicate(transaction_id)
    
    # Second occurrence should return True
    assert tracker.is_duplicate(transaction_id)


def test_transaction_tracker_max_size():
    """Test that the tracker maintains maximum tracked transactions."""
    tracker = TransactionTracker(max_tracked_transactions=3)
    
    # Add 4 unique transactions
    transactions = ["tx1", "tx2", "tx3", "tx4"]
    
    for tx in transactions:
        tracker.is_duplicate(tx)
    
    # First transaction should be removed
    assert "tx1" not in tracker._processed_transactions
    
    # Verify others are still present
    for tx in transactions[1:]:
        assert tx in tracker._processed_transactions


def test_transaction_tracker_clear():
    """Test that clear method removes all tracked transactions."""
    tracker = TransactionTracker()
    
    tracker.is_duplicate("tx1")
    tracker.is_duplicate("tx2")
    
    tracker.clear()
    
    assert len(tracker._processed_transactions) == 0


def test_transaction_id_different_types():
    """Test that the tracker works with different transaction ID types."""
    tracker = TransactionTracker()
    
    # Test with strings
    assert not tracker.is_duplicate("string_tx")
    assert tracker.is_duplicate("string_tx")
    
    # Test with integers
    assert not tracker.is_duplicate(12345)
    assert tracker.is_duplicate(12345)
    
    # Test with tuples
    assert not tracker.is_duplicate((1, 2, 3))
    assert tracker.is_duplicate((1, 2, 3))