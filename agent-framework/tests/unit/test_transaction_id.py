import pytest
from prometheus_swarm.utils.transaction_id import TransactionIDDuplicateChecker

def test_basic_duplicate_detection():
    """Test basic duplicate transaction ID detection"""
    checker = TransactionIDDuplicateChecker()
    
    # First time should return False (not a duplicate)
    assert checker.check_duplicate('tx123') is False
    
    # Second time should return True (now a duplicate)
    assert checker.check_duplicate('tx123') is True

def test_context_specific_duplicates():
    """Test duplicate checking with different contexts"""
    checker = TransactionIDDuplicateChecker()
    
    # Different contexts allow same transaction ID
    assert checker.check_duplicate('tx123', 'context1') is False
    assert checker.check_duplicate('tx123', 'context2') is False
    
    # Same transaction ID in same context is a duplicate
    assert checker.check_duplicate('tx123', 'context1') is True
    assert checker.check_duplicate('tx123', 'context2') is True

def test_reset_specific_context():
    """Test resetting a specific context"""
    checker = TransactionIDDuplicateChecker()
    
    # Add duplicates in two contexts
    assert checker.check_duplicate('tx123', 'context1') is False
    assert checker.check_duplicate('tx123', 'context2') is False
    
    # Reset context1
    checker.reset('context1')
    
    # context1 should now allow the transaction ID again
    assert checker.check_duplicate('tx123', 'context1') is False
    
    # context2 should still not allow the transaction ID
    assert checker.check_duplicate('tx123', 'context2') is True

def test_reset_all_contexts():
    """Test resetting all contexts"""
    checker = TransactionIDDuplicateChecker()
    
    # Add duplicates in multiple contexts
    assert checker.check_duplicate('tx123', 'context1') is False
    assert checker.check_duplicate('tx456', 'context2') is False
    
    # Reset all contexts
    checker.reset()
    
    # All transaction IDs should be allowed again
    assert checker.check_duplicate('tx123', 'context1') is False
    assert checker.check_duplicate('tx456', 'context2') is False

def test_invalid_transaction_id_input():
    """Test error handling for invalid transaction ID inputs"""
    checker = TransactionIDDuplicateChecker()
    
    # Empty string should raise ValueError
    with pytest.raises(ValueError, match="Transaction ID cannot be empty"):
        checker.check_duplicate('')
    
    # Non-string input should raise ValueError
    with pytest.raises(ValueError, match="Transaction ID must be a string"):
        checker.check_duplicate(123)
    with pytest.raises(ValueError, match="Transaction ID must be a string"):
        checker.check_duplicate(None)