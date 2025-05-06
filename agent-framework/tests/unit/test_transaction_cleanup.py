import pytest
from datetime import datetime, timedelta
from prometheus_swarm.utils.transaction_cleanup import cleanup_expired_transactions, _is_transaction_valid

def test_cleanup_expired_transactions_basic():
    # Create transactions with different ages
    now = datetime.now()
    old_transaction = {'timestamp': now - timedelta(hours=2)}
    recent_transaction = {'timestamp': now - timedelta(minutes=30)}
    
    transactions = [old_transaction, recent_transaction]
    
    cleaned_transactions = cleanup_expired_transactions(transactions, expiration_time_minutes=60)
    
    assert len(cleaned_transactions) == 1
    assert cleaned_transactions[0] == recent_transaction

def test_cleanup_multiple_timestamp_keys():
    now = datetime.now()
    transactions = [
        {'created_at': now - timedelta(hours=2)},  # Expired
        {'time': now - timedelta(minutes=30)},     # Valid
        {'timestamp': now - timedelta(hours=3)},   # Expired
        {'random_key': 'value'}                    # Valid by default
    ]
    
    cleaned_transactions = cleanup_expired_transactions(transactions, expiration_time_minutes=60)
    
    assert len(cleaned_transactions) == 2
    assert 'time' in cleaned_transactions[0]
    assert 'random_key' in cleaned_transactions[1]

def test_cleanup_with_string_timestamps():
    now = datetime.now()
    transactions = [
        {'timestamp': (now - timedelta(hours=2)).isoformat()},  # Expired
        {'created_at': (now - timedelta(minutes=30)).isoformat()},  # Valid
    ]
    
    cleaned_transactions = cleanup_expired_transactions(transactions, expiration_time_minutes=60)
    
    assert len(cleaned_transactions) == 1
    assert cleaned_transactions[0]['created_at'] == transactions[1]['created_at']

def test_invalid_expiration_time():
    transactions = [{'timestamp': datetime.now()}]
    
    with pytest.raises(ValueError, match="Expiration time must be a positive integer"):
        cleanup_expired_transactions(transactions, expiration_time_minutes=-1)
    
    with pytest.raises(ValueError, match="Expiration time must be a positive integer"):
        cleanup_expired_transactions(transactions, expiration_time_minutes=0)
    
    with pytest.raises(ValueError, match="Expiration time must be a positive integer"):
        cleanup_expired_transactions(transactions, expiration_time_minutes="invalid")

def test_is_transaction_valid():
    now = datetime.now()
    expiration_threshold = now - timedelta(hours=1)
    
    # Valid cases
    assert _is_transaction_valid({'timestamp': now}, expiration_threshold) == True
    assert _is_transaction_valid({'created_at': now}, expiration_threshold) == True
    assert _is_transaction_valid({'random_key': 'value'}, expiration_threshold) == True
    
    # Invalid cases
    assert _is_transaction_valid({'timestamp': now - timedelta(hours=2)}, expiration_threshold) == False

def test_transaction_with_invalid_timestamp_string():
    now = datetime.now()
    expiration_threshold = now - timedelta(hours=1)
    
    # Invalid timestamp string should be skipped
    assert _is_transaction_valid({'timestamp': 'invalid-date'}, expiration_threshold) == True