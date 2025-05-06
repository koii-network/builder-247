import pytest
import datetime
from src.transaction_cleanup import TransactionIdCleanupJob

def test_cleanup_transaction_ids_basic():
    """Test basic transaction cleanup functionality"""
    now = datetime.datetime(2023, 1, 15)
    transactions = [
        {'id': 1, 'timestamp': now - datetime.timedelta(days=10)},
        {'id': 2, 'timestamp': now - datetime.timedelta(days=40)},
        {'id': 3, 'timestamp': now - datetime.timedelta(days=20)}
    ]
    
    cleaned = TransactionIdCleanupJob.cleanup_transaction_ids(
        transactions, 
        max_age_days=30, 
        current_time=now
    )
    
    assert len(cleaned) == 2
    assert all(transaction['id'] in [1, 3] for transaction in cleaned)

def test_cleanup_transaction_ids_no_timestamp():
    """Test handling of transactions without timestamp"""
    now = datetime.datetime(2023, 1, 15)
    transactions = [
        {'id': 1},
        {'id': 2},
        {'id': 3, 'timestamp': now - datetime.timedelta(days=10)}
    ]
    
    cleaned = TransactionIdCleanupJob.cleanup_transaction_ids(
        transactions, 
        max_age_days=30, 
        current_time=now
    )
    
    assert len(cleaned) == 3  # All transactions kept if no timestamp

def test_cleanup_transaction_ids_negative_max_age():
    """Test raising ValueError for negative max_age_days"""
    with pytest.raises(ValueError, match="Max age days must be non-negative"):
        TransactionIdCleanupJob.cleanup_transaction_ids(
            [], 
            max_age_days=-1
        )

def test_cleanup_transaction_ids_empty_list():
    """Test cleanup with an empty transaction list"""
    cleaned = TransactionIdCleanupJob.cleanup_transaction_ids([])
    assert cleaned == []

def test_transaction_age_calculation():
    """Test precise age calculation"""
    now = datetime.datetime(2023, 1, 15)
    transactions = [
        {'id': 1, 'timestamp': now - datetime.timedelta(days=29, hours=23)},
        {'id': 2, 'timestamp': now - datetime.timedelta(days=30, hours=1)}
    ]
    
    cleaned = TransactionIdCleanupJob.cleanup_transaction_ids(
        transactions, 
        max_age_days=30, 
        current_time=now
    )
    
    assert len(cleaned) == 1
    assert cleaned[0]['id'] == 1