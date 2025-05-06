import pytest
from prometheus_swarm.utils.transaction_id import TransactionIDChecker

def test_transaction_id_checker_basic_functionality():
    """
    Test basic functionality of the TransactionIDChecker.
    """
    checker = TransactionIDChecker()
    
    # Add first transaction ID
    checker.add_transaction_id("transaction1")
    assert checker.get_tracked_count() == 1
    assert checker.is_duplicate("transaction1") == True
    
    # Add second transaction ID
    checker.add_transaction_id("transaction2")
    assert checker.get_tracked_count() == 2
    assert checker.is_duplicate("transaction2") == True

def test_transaction_id_checker_duplicate_prevention():
    """
    Test that duplicate transaction IDs are prevented.
    """
    checker = TransactionIDChecker()
    
    # First add is successful
    checker.add_transaction_id("unique_transaction")
    
    # Attempting to add same transaction ID should raise ValueError
    with pytest.raises(ValueError, match="Duplicate transaction ID"):
        checker.add_transaction_id("unique_transaction")

def test_transaction_id_checker_none_handling():
    """
    Test handling of None transaction IDs.
    """
    checker = TransactionIDChecker()
    
    # Attempting to add None should raise TypeError
    with pytest.raises(TypeError, match="Transaction ID cannot be None"):
        checker.add_transaction_id(None)
    
    # Checking None should raise TypeError
    with pytest.raises(TypeError, match="Transaction ID cannot be None"):
        checker.is_duplicate(None)

def test_transaction_id_checker_different_types():
    """
    Test that different type transaction IDs work correctly.
    """
    checker = TransactionIDChecker()
    
    # Integers
    checker.add_transaction_id(12345)
    assert checker.is_duplicate(12345) == True
    
    # Strings
    checker.add_transaction_id("string_id")
    assert checker.is_duplicate("string_id") == True
    
    # Tuples
    checker.add_transaction_id((1, 2, 3))
    assert checker.is_duplicate((1, 2, 3)) == True

def test_transaction_id_checker_clear_method():
    """
    Test the clear method of TransactionIDChecker.
    """
    checker = TransactionIDChecker()
    
    checker.add_transaction_id("transaction1")
    checker.add_transaction_id("transaction2")
    assert checker.get_tracked_count() == 2
    
    # Clear the tracked IDs
    checker.clear()
    assert checker.get_tracked_count() == 0
    
    # These should now be considered not duplicate
    assert checker.is_duplicate("transaction1") == False
    assert checker.is_duplicate("transaction2") == False