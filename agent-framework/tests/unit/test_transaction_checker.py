import pytest
from prometheus_swarm.utils.transaction_checker import TransactionDuplicationChecker

def test_transaction_duplication_checker_basic():
    """
    Test basic functionality of the TransactionDuplicationChecker.
    """
    checker = TransactionDuplicationChecker()
    
    # First time adding a transaction ID should return True
    assert checker.add_transaction('tx_001') == True
    
    # Second time adding the same transaction ID should return False
    assert checker.add_transaction('tx_001') == False
    
    # Duplicate check should return True for existing transaction ID
    assert checker.is_duplicate('tx_001') == True

def test_transaction_duplication_checker_multiple_ids():
    """
    Test handling multiple unique and duplicate transaction IDs.
    """
    checker = TransactionDuplicationChecker()
    
    # Add multiple unique transaction IDs
    assert checker.add_transaction('tx_001') == True
    assert checker.add_transaction('tx_002') == True
    assert checker.add_transaction('tx_003') == True
    
    # Attempt to add duplicate transaction IDs
    assert checker.add_transaction('tx_001') == False
    assert checker.add_transaction('tx_002') == False

def test_transaction_duplication_checker_clear():
    """
    Test clearing of transaction IDs.
    """
    checker = TransactionDuplicationChecker()
    
    # Add a transaction ID
    assert checker.add_transaction('tx_001') == True
    assert checker.is_duplicate('tx_001') == True
    
    # Clear transaction IDs
    checker.clear()
    
    # Transaction ID should no longer be considered a duplicate
    assert checker.is_duplicate('tx_001') == False
    assert checker.add_transaction('tx_001') == True

def test_get_unique_transactions():
    """
    Test filtering unique transactions from a list.
    """
    checker = TransactionDuplicationChecker()
    
    transactions = [
        {'transaction_id': 'tx_001', 'amount': 100},
        {'transaction_id': 'tx_002', 'amount': 200},
        {'transaction_id': 'tx_001', 'amount': 300},  # Duplicate
        {'transaction_id': 'tx_003', 'amount': 400},
        {'amount': 500}  # No transaction ID
    ]
    
    unique_transactions = checker.get_unique_transactions(transactions)
    
    # Should only return first occurrence of each transaction ID and transactions without ID
    assert len(unique_transactions) == 4
    assert unique_transactions[0]['amount'] == 100
    assert unique_transactions[1]['amount'] == 200
    assert unique_transactions[2]['amount'] == 400
    assert unique_transactions[3]['amount'] == 500

def test_get_unique_transactions_custom_key():
    """
    Test get_unique_transactions with a custom ID key.
    """
    checker = TransactionDuplicationChecker()
    
    transactions = [
        {'custom_id': 'tx_001', 'amount': 100},
        {'custom_id': 'tx_002', 'amount': 200},
        {'custom_id': 'tx_001', 'amount': 300}  # Duplicate
    ]
    
    unique_transactions = checker.get_unique_transactions(transactions, id_key='custom_id')
    
    # Should only return first occurrence of each transaction ID
    assert len(unique_transactions) == 2
    assert unique_transactions[0]['amount'] == 100
    assert unique_transactions[1]['amount'] == 200