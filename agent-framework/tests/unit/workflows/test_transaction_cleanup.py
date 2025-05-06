"""
Unit tests for Transaction Cleanup Job
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from prometheus_swarm.workflows.transaction_cleanup import (
    TransactionCleanupJob, 
    run_transaction_cleanup
)
from prometheus_swarm.database.models import Transaction
from prometheus_swarm.database.database import SessionLocal

class MockTransaction:
    def __init__(self, created_at):
        self.created_at = created_at

@pytest.fixture
def mock_session():
    with patch('prometheus_swarm.workflows.transaction_cleanup.SessionLocal') as mock_session_local:
        mock_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_session
        yield mock_session

def test_transaction_cleanup_job_initialization():
    job = TransactionCleanupJob(retention_days=45, max_delete_batch=500)
    assert job.retention_days == 45
    assert job.max_delete_batch == 500

def test_clean_old_transactions(mock_session):
    # Arrange
    old_date = datetime.utcnow() - timedelta(days=31)
    mock_transactions = [MockTransaction(created_at=old_date) for _ in range(10)]
    
    mock_session.query().filter().limit().all.return_value = mock_transactions
    
    # Act
    job = TransactionCleanupJob(retention_days=30)
    deleted_count = job.clean_old_transactions()
    
    # Assert
    assert deleted_count == 10
    assert mock_session.delete.call_count == 10
    mock_session.commit.assert_called_once()

def test_run_transaction_cleanup(mock_session):
    old_date = datetime.utcnow() - timedelta(days=31)
    mock_transactions = [MockTransaction(created_at=old_date) for _ in range(5)]
    
    mock_session.query().filter().limit().all.return_value = mock_transactions
    
    deleted_count = run_transaction_cleanup()
    
    assert deleted_count == 5

def test_transaction_cleanup_error_handling(mock_session):
    mock_session.query().filter().limit().all.side_effect = Exception("Database error")
    
    with pytest.raises(Exception, match="Database error"):
        run_transaction_cleanup()

def test_edge_cases_retention_days(mock_session):
    # Test with custom retention days
    job = TransactionCleanupJob(retention_days=60)
    assert job.retention_days == 60

def test_edge_cases_max_delete_batch(mock_session):
    # Test with custom max delete batch
    job = TransactionCleanupJob(max_delete_batch=2000)
    assert job.max_delete_batch == 2000