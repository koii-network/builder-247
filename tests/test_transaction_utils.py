import pytest
from src.transaction_utils import (
    check_transaction_id_duplicate, 
    add_transaction_with_duplicate_check, 
    TransactionDuplicationError
)

def test_check_transaction_id_duplicate_no_duplicates():
    transactions = [
        {'transaction_id': '001', 'amount': 100},
        {'transaction_id': '002', 'amount': 200}
    ]
    assert not check_transaction_id_duplicate(transactions, '003')

def test_check_transaction_id_duplicate_with_duplicates():
    transactions = [
        {'transaction_id': '001', 'amount': 100},
        {'transaction_id': '002', 'amount': 200}
    ]
    assert check_transaction_id_duplicate(transactions, '001')

def test_check_transaction_id_duplicate_empty_list():
    transactions = []
    assert not check_transaction_id_duplicate(transactions, '001')

def test_check_transaction_id_duplicate_invalid_inputs():
    with pytest.raises(ValueError, match="Transactions list cannot be None"):
        check_transaction_id_duplicate(None, '001')
    
    with pytest.raises(ValueError, match="Transaction ID cannot be empty"):
        check_transaction_id_duplicate([], '')

def test_add_transaction_with_duplicate_check_success():
    transactions = [
        {'transaction_id': '001', 'amount': 100}
    ]
    new_transaction = {'transaction_id': '002', 'amount': 200}
    
    updated_transactions = add_transaction_with_duplicate_check(transactions, new_transaction)
    
    assert len(updated_transactions) == 2
    assert updated_transactions[-1] == new_transaction

def test_add_transaction_with_duplicate_check_duplicate_raises_error():
    transactions = [
        {'transaction_id': '001', 'amount': 100}
    ]
    duplicate_transaction = {'transaction_id': '001', 'amount': 250}
    
    with pytest.raises(TransactionDuplicationError):
        add_transaction_with_duplicate_check(transactions, duplicate_transaction)

def test_add_transaction_with_duplicate_check_empty_list():
    new_transaction = {'transaction_id': '001', 'amount': 100}
    
    updated_transactions = add_transaction_with_duplicate_check(None, new_transaction)
    
    assert len(updated_transactions) == 1
    assert updated_transactions[0] == new_transaction

def test_add_transaction_with_duplicate_check_invalid_inputs():
    with pytest.raises(ValueError, match="Transaction must have a transaction_id"):
        add_transaction_with_duplicate_check([], {'amount': 100})
    
    with pytest.raises(ValueError, match="New transaction must be a dictionary"):
        add_transaction_with_duplicate_check([], "Not a dictionary")