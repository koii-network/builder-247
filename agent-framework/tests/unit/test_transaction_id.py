import pytest
from prometheus_swarm.utils.transaction_id import TransactionIdChecker

def test_no_duplicates():
    """Test that no duplicates are found when transaction IDs are unique."""
    transactions = [
        {'transaction_id': '1', 'data': 'a'},
        {'transaction_id': '2', 'data': 'b'},
        {'transaction_id': '3', 'data': 'c'}
    ]
    
    duplicates = TransactionIdChecker.check_duplicates(transactions)
    assert len(duplicates) == 0

def test_with_duplicates():
    """Test detecting duplicate transaction IDs."""
    transactions = [
        {'transaction_id': '1', 'data': 'a'},
        {'transaction_id': '2', 'data': 'b'},
        {'transaction_id': '1', 'data': 'c'},
        {'transaction_id': '3', 'data': 'd'},
        {'transaction_id': '2', 'data': 'e'}
    ]
    
    duplicates = TransactionIdChecker.check_duplicates(transactions)
    assert len(duplicates) == 2
    assert duplicates[0]['transaction_id'] == '1'
    assert duplicates[1]['transaction_id'] == '2'

def test_empty_list():
    """Test handling an empty list of transactions."""
    transactions = []
    
    duplicates = TransactionIdChecker.check_duplicates(transactions)
    assert len(duplicates) == 0

def test_missing_transaction_id():
    """Test that a ValueError is raised when a transaction is missing a transaction ID."""
    transactions = [
        {'transaction_id': '1', 'data': 'a'},
        {'data': 'b'}
    ]
    
    with pytest.raises(ValueError, match="Transaction is missing 'transaction_id' key"):
        TransactionIdChecker.check_duplicates(transactions)

def test_ensure_unique_transactions():
    """Test removing duplicate transactions while preserving order."""
    transactions = [
        {'transaction_id': '1', 'data': 'a'},
        {'transaction_id': '2', 'data': 'b'},
        {'transaction_id': '1', 'data': 'c'},
        {'transaction_id': '3', 'data': 'd'},
        {'transaction_id': '2', 'data': 'e'}
    ]
    
    unique_transactions = TransactionIdChecker.ensure_unique_transactions(transactions)
    
    assert len(unique_transactions) == 3
    assert [t['transaction_id'] for t in unique_transactions] == ['1', '2', '3']
    
    # Ensure the first occurrence of each transaction ID is kept
    assert unique_transactions[0]['data'] == 'a'
    assert unique_transactions[1]['data'] == 'b'
    assert unique_transactions[2]['data'] == 'd'

def test_ensure_unique_transactions_empty():
    """Test ensuring unique transactions with an empty list."""
    transactions = []
    
    unique_transactions = TransactionIdChecker.ensure_unique_transactions(transactions)
    assert len(unique_transactions) == 0

def test_ensure_unique_transactions_missing_transaction_id():
    """Test that a ValueError is raised when a transaction is missing a transaction ID."""
    transactions = [
        {'transaction_id': '1', 'data': 'a'},
        {'data': 'b'}
    ]
    
    with pytest.raises(ValueError, match="Transaction is missing 'transaction_id' key"):
        TransactionIdChecker.ensure_unique_transactions(transactions)