import pytest
import time
from datetime import datetime, timedelta
from prometheus_swarm.utils.transaction_cleanup import TransactionExpirationCleaner

def test_transaction_expiration_basic():
    """
    Test basic transaction expiration functionality.
    """
    cleaner = TransactionExpirationCleaner(expiration_time_seconds=1)
    
    # Add some transactions
    cleaner.add_transaction("Transaction 1")
    cleaner.add_transaction("Transaction 2")
    
    # Wait for expiration
    time.sleep(1.5)
    
    # Clean expired transactions
    expired = cleaner.clean_expired_transactions()
    
    assert len(expired) == 2
    assert cleaner.get_current_transaction_count() == 0

def test_transaction_expiration_partial():
    """
    Test partial transaction expiration.
    """
    cleaner = TransactionExpirationCleaner(expiration_time_seconds=2)
    
    # Add transactions
    cleaner.add_transaction("Transaction 1")
    time.sleep(1)
    cleaner.add_transaction("Transaction 2")
    time.sleep(1.5)
    
    # Clean expired transactions
    expired = cleaner.clean_expired_transactions()
    
    assert len(expired) == 1
    assert cleaner.get_current_transaction_count() == 1

def test_transaction_expiration_none():
    """
    Test no transaction expiration when time hasn't elapsed.
    """
    cleaner = TransactionExpirationCleaner(expiration_time_seconds=5)
    
    # Add transactions
    cleaner.add_transaction("Transaction 1")
    cleaner.add_transaction("Transaction 2")
    
    # Clean transactions (no time elapsed)
    expired = cleaner.clean_expired_transactions()
    
    assert len(expired) == 0
    assert cleaner.get_current_transaction_count() == 2

def test_transaction_expiration_custom_objects():
    """
    Test expiration with custom transaction objects.
    """
    class CustomTransaction:
        def __init__(self, id):
            self.id = id
    
    cleaner = TransactionExpirationCleaner(expiration_time_seconds=1)
    
    # Add custom transaction objects
    transaction1 = CustomTransaction(1)
    transaction2 = CustomTransaction(2)
    
    cleaner.add_transaction(transaction1)
    cleaner.add_transaction(transaction2)
    
    # Wait for expiration
    time.sleep(1.5)
    
    # Clean expired transactions
    expired = cleaner.clean_expired_transactions()
    
    assert len(expired) == 2
    assert all(isinstance(t, CustomTransaction) for t in expired)
    assert cleaner.get_current_transaction_count() == 0

def test_transaction_expiration_edge_cases():
    """
    Test edge cases in transaction expiration.
    """
    # Zero expiration time
    cleaner_zero = TransactionExpirationCleaner(expiration_time_seconds=0)
    cleaner_zero.add_transaction("Transaction")
    
    expired_zero = cleaner_zero.clean_expired_transactions()
    assert len(expired_zero) == 1

    # Very long expiration time
    cleaner_long = TransactionExpirationCleaner(expiration_time_seconds=3600)
    cleaner_long.add_transaction("Transaction")
    
    expired_long = cleaner_long.clean_expired_transactions()
    assert len(expired_long) == 0