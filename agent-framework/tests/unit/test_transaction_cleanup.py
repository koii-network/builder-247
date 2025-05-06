import pytest
import datetime
from unittest.mock import patch, MagicMock
from agent-framework.prometheus_swarm.utils.transaction_cleanup import cleanup_expired_transactions
from agent-framework.prometheus_swarm.database.models import Transaction

@pytest.fixture
def mock_db_session():
    with patch('agent-framework.prometheus_swarm.database.database.get_database_session') as mock_session:
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        yield mock_session_instance

def test_cleanup_expired_transactions(mock_db_session):
    # Create mock expired transactions
    expiration_threshold_hours = 24
    expired_timestamp = datetime.datetime.utcnow() - datetime.timedelta(hours=expiration_threshold_hours + 1)
    
    mock_transactions = [
        MagicMock(spec=Transaction, created_at=expired_timestamp),
        MagicMock(spec=Transaction, created_at=expired_timestamp)
    ]
    
    # Configure the mock query to return the expired transactions
    mock_db_session.query().filter().limit().all.return_value = mock_transactions
    
    # Call the cleanup function
    result = cleanup_expired_transactions(expiration_threshold_hours)
    
    # Verify the results
    assert result['status'] == 'success'
    assert result['deleted_transactions'] == 2
    
    # Check that delete was called on each transaction
    assert mock_db_session.delete.call_count == 2
    mock_db_session.commit.assert_called_once()

def test_cleanup_no_expired_transactions(mock_db_session):
    # Configure the mock query to return no transactions
    mock_db_session.query().filter().limit().all.return_value = []
    
    # Call the cleanup function
    result = cleanup_expired_transactions()
    
    # Verify the results
    assert result['status'] == 'success'
    assert result['deleted_transactions'] == 0
    
    # Ensure no delete or commit operations occurred
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_called_once()

def test_cleanup_database_error(mock_db_session):
    # Simulate a database error during cleanup
    mock_db_session.query().filter().limit().all.side_effect = Exception("Database error")
    
    # Call the cleanup function
    result = cleanup_expired_transactions()
    
    # Verify the results
    assert result['status'] == 'error'
    assert 'Database error' in result['message']
    assert result['deleted_transactions'] == 0
    
    # Ensure rollback was called
    mock_db_session.rollback.assert_called_once()

def test_cleanup_max_batch_size(mock_db_session):
    # Create many expired transactions
    expiration_threshold_hours = 24
    expired_timestamp = datetime.datetime.utcnow() - datetime.timedelta(hours=expiration_threshold_hours + 1)
    
    mock_transactions = [
        MagicMock(spec=Transaction, created_at=expired_timestamp) for _ in range(1500)
    ]
    
    # Configure the mock query to return transactions
    mock_db_session.query().filter().limit().all.return_value = mock_transactions[:1000]
    
    # Call the cleanup function with default max batch size
    result = cleanup_expired_transactions(expiration_threshold_hours)
    
    # Verify the results
    assert result['status'] == 'success'
    assert result['deleted_transactions'] == 1000
    
    # Check that delete was called 1000 times (max batch size)
    assert mock_db_session.delete.call_count == 1000
    mock_db_session.commit.assert_called_once()