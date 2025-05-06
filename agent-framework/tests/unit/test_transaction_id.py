import pytest
import threading
import time
from prometheus_swarm.utils.transaction_id import TransactionIDManager

def test_transaction_id_generation():
    """Test that transaction IDs are unique."""
    manager = TransactionIDManager()
    transaction_ids = set(manager.generate_transaction_id() for _ in range(1000))
    assert len(transaction_ids) == 1000, "Transaction IDs must be unique"

def test_submit_transaction():
    """Test transaction submission."""
    manager = TransactionIDManager()
    transaction_data = {'payload': 'test_data'}
    transaction_id = manager.submit_transaction(transaction_data)
    
    assert transaction_id is not None
    status = manager.get_transaction_status(transaction_id)
    assert status is not None
    assert status['data'] == transaction_data
    assert status['status'] == 'pending'

def test_update_transaction_status():
    """Test updating transaction status."""
    manager = TransactionIDManager()
    transaction_id = manager.submit_transaction({'payload': 'test'})
    
    result = manager.update_transaction_status(transaction_id, 'completed')
    assert result is True
    
    status = manager.get_transaction_status(transaction_id)
    assert status['status'] == 'completed'

def test_concurrent_transaction_submission():
    """Test concurrent transaction submissions."""
    manager = TransactionIDManager()
    transaction_ids = []
    
    def submit_transaction():
        transaction_data = {'thread_id': threading.get_ident()}
        transaction_ids.append(manager.submit_transaction(transaction_data))
    
    threads = [threading.Thread(target=submit_transaction) for _ in range(100)]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    assert len(set(transaction_ids)) == 100, "Each thread should generate a unique transaction ID"

def test_thread_safe_transaction_retrieval():
    """Test thread-safe transaction retrieval."""
    manager = TransactionIDManager()
    shared_results = []
    
    def retrieve_transaction(transaction_id):
        status = manager.get_transaction_status(transaction_id)
        shared_results.append(status)
    
    transaction_id = manager.submit_transaction({'payload': 'test'})
    
    threads = [threading.Thread(target=retrieve_transaction, args=(transaction_id,)) for _ in range(50)]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # All threads should retrieve the same transaction details
    assert all(result == shared_results[0] for result in shared_results)

def test_nonexistent_transaction():
    """Test behavior when retrieving a nonexistent transaction."""
    manager = TransactionIDManager()
    status = manager.get_transaction_status('nonexistent_id')
    assert status is None