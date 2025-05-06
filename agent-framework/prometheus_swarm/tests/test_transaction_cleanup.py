import pytest
from datetime import datetime, timedelta
from prometheus_swarm.utils.transaction_cleanup import (
    cleanup_expired_transactions, 
    TransactionCleanupError,
    _is_transaction_valid
)

@pytest.fixture
def sample_transactions():
    current_time = datetime.now()
    return [
        {
            'id': 1, 
            'timestamp': (current_time - timedelta(hours=25)).isoformat(),
            'data': 'Expired transaction'
        },
        {
            'id': 2, 
            'timestamp': (current_time - timedelta(hours=23)).isoformat(),
            'data': 'Valid transaction'
        },
        {
            'id': 3, 
            'timestamp': current_time.isoformat(),
            'data': 'Fresh transaction'
        }
    ]

def test_cleanup_expired_transactions(sample_transactions):
    cleaned_transactions = cleanup_expired_transactions(sample_transactions, expiration_hours=24)
    
    assert len(cleaned_transactions) == 2
    assert all(t['id'] != 1 for t in cleaned_transactions)

def test_cleanup_invalid_input():
    with pytest.raises(TransactionCleanupError):
        cleanup_expired_transactions(None)
    
    with pytest.raises(TransactionCleanupError):
        cleanup_expired_transactions([], expiration_hours=0)

def test_transaction_validation():
    current_time = datetime.now()
    
    valid_transaction = {
        'timestamp': (current_time - timedelta(hours=12)).isoformat()
    }
    
    invalid_transaction = {
        'timestamp': (current_time - timedelta(hours=36)).isoformat()
    }
    
    assert _is_transaction_valid(valid_transaction, current_time, 24)
    assert not _is_transaction_valid(invalid_transaction, current_time, 24)

def test_edge_cases():
    current_time = datetime.now()
    
    # Test missing timestamp
    assert not _is_transaction_valid({}, current_time, 24)
    
    # Test invalid timestamp format
    assert not _is_transaction_valid({'timestamp': 'invalid'}, current_time, 24)

def test_custom_expiration_hours(sample_transactions):
    cleaned_transactions = cleanup_expired_transactions(sample_transactions, expiration_hours=48)
    
    assert len(cleaned_transactions) == 3  # All transactions are valid

def test_multiple_transactions():
    current_time = datetime.now()
    transactions = [
        {'id': i, 'timestamp': (current_time - timedelta(hours=i*10)).isoformat()}
        for i in range(5)
    ]
    
    cleaned_transactions = cleanup_expired_transactions(transactions, expiration_hours=36)
    
    assert len(cleaned_transactions) == 4  # 4 out of 5 transactions are valid