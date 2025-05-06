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
    Test duplicate detection works with different data types.
    """
    manager = TransactionIDManager()
    
    # Different types of transaction IDs
    assert not manager.is_duplicate(123)  # Integer
    assert manager.is_duplicate(123)      # Integer is a duplicate
    
    assert not manager.is_duplicate("123")  # String
    assert manager.is_duplicate("123")      # String is a duplicate
    
    assert not manager.is_duplicate(["list_transaction"])
    assert manager.is_duplicate(["list_transaction"])

def test_transaction_id_cache_size_limit():
    """
    Test that the cache size limit prevents unbounded memory growth.
    """
    # Small cache size for testing
    manager = TransactionIDManager(max_cache_size=3)
    
    # Add 3 unique transaction IDs
    ids = ["tx1", "tx2", "tx3"]
    for tx_id in ids:
        assert not manager.is_duplicate(tx_id)
    
    # Add a 4th transaction (should remove the oldest)
    assert not manager.is_duplicate("tx4")
    
    # First transaction should be considered a duplicate now
    assert manager.is_duplicate("tx1")

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