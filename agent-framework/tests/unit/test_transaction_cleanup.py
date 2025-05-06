import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Create a mock TransactionLog since we can't rely on database models
class TransactionLog:
    def __init__(self, id, created_at):
        self.id = id
        self.created_at = created_at

from prometheus_swarm.workflows.transaction_cleanup import TransactionCleanupJob

class MockSession:
    def __init__(self, transactions):
        self.transactions = transactions
        self.deleted_transactions = []
        
    def query(self, model):
        return self
    
    def filter(self, condition):
        filtered_transactions = [t for t in self.transactions if condition._evaluate_obj(t)]
        self.transactions = filtered_transactions
        return self
    
    def limit(self, limit):
        return self
    
    def all(self):
        return self.transactions
    
    def delete(self, transaction):
        self.deleted_transactions.append(transaction)
    
    def commit(self):
        for t in self.deleted_transactions:
            self.transactions.remove(t)
        self.deleted_transactions = []
    
    def close(self):
        pass

def create_mock_transaction(days_old):
    return TransactionLog(
        id=1, 
        created_at=datetime.utcnow() - timedelta(days=days_old)
    )

def test_transaction_cleanup_job_no_old_logs():
    # Test scenario with no old logs
    deleted_count = TransactionCleanupJob.cleanup_old_transactions(
        session_factory=lambda: MockSession([])
    )
    assert deleted_count == 0

def test_transaction_cleanup_job_with_old_logs():
    # Prepare mock transactions - some old, some recent
    current_time = datetime.utcnow()
    transactions = [
        create_mock_transaction(40),  # Will be deleted
        create_mock_transaction(35),  # Will be deleted
        create_mock_transaction(20),  # Will be kept
        create_mock_transaction(10)   # Will be kept
    ]
    
    deleted_count = TransactionCleanupJob.cleanup_old_transactions(
        retention_days=30,
        session_factory=lambda: MockSession(transactions)
    )
    
    assert deleted_count == 2

def test_transaction_cleanup_job_large_dataset():
    # Simulate a large dataset with more than max_delete_batch
    transactions = [
        create_mock_transaction(40) for _ in range(15000)
    ]
    
    deleted_count = TransactionCleanupJob.cleanup_old_transactions(
        retention_days=30,
        max_delete_batch=10000,
        session_factory=lambda: MockSession(transactions)
    )
    
    assert deleted_count == 15000

def test_transaction_cleanup_job_exception_handling():
    def raise_exception():
        raise Exception("Database connection error")
    
    deleted_count = TransactionCleanupJob.cleanup_old_transactions(
        session_factory=raise_exception
    )
    assert deleted_count == 0