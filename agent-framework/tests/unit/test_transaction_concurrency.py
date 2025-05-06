import pytest
import threading
from typing import List
from prometheus_swarm.utils.transaction_concurrency import TransactionIDManager

def test_unique_transaction_id_generation():
    """Test that generated transaction IDs are unique."""
    manager = TransactionIDManager()
    transaction_ids = set()
    
    def generate_ids(n_ids: int, results: List[str]):
        for _ in range(n_ids):
            results.append(manager.generate_transaction_id())
    
    threads = []
    thread_results = [[] for _ in range(5)]
    
    for i in range(5):
        thread = threading.Thread(target=generate_ids, args=(10, thread_results[i]))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Flatten results
    all_ids = [tid for thread_list in thread_results for tid in thread_list]
    transaction_ids.update(all_ids)
    
    assert len(transaction_ids) == 50, "All generated IDs should be unique"

def test_concurrent_transaction_registration():
    """Test concurrent transaction registration."""
    manager = TransactionIDManager()
    successes = [0]
    failures = [0]
    
    def register_transaction(tid: str, success_counter, failure_counter):
        if manager.register_transaction(tid):
            with success_counter[0] += 1
            pass
        else:
            with failure_counter[0] += 1
            pass
    
    # Try to register the same transaction ID across multiple threads
    threads = []
    transaction_id = manager.generate_transaction_id()
    
    for _ in range(10):
        thread = threading.Thread(target=register_transaction, 
                                  args=(transaction_id, successes, failures))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    assert successes[0] == 1, "Only one thread should successfully register the transaction"
    assert failures[0] == 9, "Other threads should fail to register"

def test_concurrent_transaction_state_update():
    """Test concurrent transaction state updates."""
    manager = TransactionIDManager()
    transaction_id = manager.generate_transaction_id()
    manager.register_transaction(transaction_id)
    
    states = []
    
    def update_state(state: str):
        manager.update_transaction_state(transaction_id, state)
        states.append(state)
    
    threads = []
    test_states = ['processing', 'completed', 'error', 'rolled_back', 'finalized']
    
    for state in test_states:
        thread = threading.Thread(target=update_state, args=(state,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    final_state = manager.get_transaction_state(transaction_id)
    assert final_state in test_states, "Transaction should have a valid final state"

def test_thread_safe_transaction_tracking():
    """Test thread-safe tracking of multiple transactions."""
    manager = TransactionIDManager()
    
    def create_and_track_transaction():
        tid = manager.generate_transaction_id()
        manager.register_transaction(tid)
        manager.update_transaction_state(tid, 'processing')
        manager.complete_transaction(tid)
    
    threads = []
    for _ in range(100):
        thread = threading.Thread(target=create_and_track_transaction)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # No assertions needed - if no race conditions occur, the test passes

def test_reset_functionality():
    """Test reset functionality of the transaction manager."""
    manager = TransactionIDManager()
    
    # Register some transactions
    transaction_ids = [manager.generate_transaction_id() for _ in range(10)]
    for tid in transaction_ids:
        manager.register_transaction(tid)
    
    # Check registered state
    for tid in transaction_ids:
        assert manager.get_transaction_state(tid) is not None
    
    # Reset
    manager.reset()
    
    # Check that all transactions are cleared
    for tid in transaction_ids:
        assert manager.get_transaction_state(tid) is None

def test_state_transitions():
    """Test transaction state transitions."""
    manager = TransactionIDManager()
    
    # Generate and register a transaction
    transaction_id = manager.generate_transaction_id()
    assert manager.register_transaction(transaction_id)
    
    # Check initial state
    assert manager.get_transaction_state(transaction_id) == 'pending'
    
    # Update states
    assert manager.update_transaction_state(transaction_id, 'processing')
    assert manager.get_transaction_state(transaction_id) == 'processing'
    
    # Complete transaction
    assert manager.complete_transaction(transaction_id)
    assert manager.get_transaction_state(transaction_id) == 'completed'
    
    # Try to complete an unknown transaction
    unknown_id = manager.generate_transaction_id()
    assert not manager.complete_transaction(unknown_id)