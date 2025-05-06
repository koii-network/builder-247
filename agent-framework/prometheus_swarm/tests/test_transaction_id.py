import pytest
from prometheus_swarm.utils.transaction_id import TransactionIDManager

def test_transaction_id_duplicate_detection():
    """
    Test basic duplicate transaction ID detection.
    """
    manager = TransactionIDManager()
    
    # First occurrence should return False (not a duplicate)
    assert not manager.is_duplicate("transaction_1")
    
    # Same transaction ID should now return True (duplicate)
    assert manager.is_duplicate("transaction_1")

def test_transaction_id_with_different_types():
    """
    Test duplicate detection with different data types.
    """
    manager = TransactionIDManager()
    
    # Demonstrate type-sensitive duplicate detection
    assert not manager.is_duplicate(123)
    assert not manager.is_duplicate("123")  # Ensure these are treated as distinct
    assert manager.is_duplicate(123)
    assert manager.is_duplicate("123")
    
    # Complex types
    assert not manager.is_duplicate(["list_transaction"])
    assert manager.is_duplicate(["list_transaction"])

def test_transaction_id_cache_size_limit():
    """
    Test that the cache size limit prevents unbounded memory growth.
    """
    # Small cache size for testing
    manager = TransactionIDManager(max_cache_size=3)
    
    # Add transactions that will push out older entries
    assert not manager.is_duplicate("tx1")
    assert not manager.is_duplicate("tx2")
    assert not manager.is_duplicate("tx3")
    assert not manager.is_duplicate("tx4")
    
    # tx1 should now be considered a new transaction
    assert not manager.is_duplicate("tx1")

def test_transaction_id_clear_method():
    """
    Test the clear method resets the transaction ID tracking.
    """
    manager = TransactionIDManager()
    
    # Add some transaction IDs
    assert not manager.is_duplicate("tx1")
    assert manager.is_duplicate("tx1")
    
    # Clear the manager
    manager.clear()
    
    # Transaction ID should now be allowed again
    assert not manager.is_duplicate("tx1")