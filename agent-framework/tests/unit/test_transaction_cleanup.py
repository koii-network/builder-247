import pytest
from unittest.mock import patch, MagicMock
import datetime

from agent-framework.prometheus_swarm.utils.transaction_cleanup import (
    cleanup_expired_transactions,
    configure_transaction_cleanup_job
)

@pytest.fixture
def mock_database():
    with patch('agent-framework.prometheus_swarm.database.database.get_database_connection') as mock_db:
        yield mock_db

def test_cleanup_expired_transactions_no_transactions(mock_database):
    # Setup: No expired transactions
    mock_db_instance = MagicMock()
    mock_db_instance.query.return_value = []
    mock_database.return_value = mock_db_instance

    result = cleanup_expired_transactions()

    assert result['status'] == 'success'
    assert result['deleted_count'] == 0
    mock_db_instance.query.assert_called_once()
    mock_db_instance.delete.assert_not_called()

def test_cleanup_expired_transactions_with_transactions(mock_database):
    # Setup: Some expired transactions
    mock_db_instance = MagicMock()
    mock_transaction = MagicMock()
    mock_transaction.id = 1
    mock_db_instance.query.return_value = [mock_transaction]
    mock_db_instance.delete.return_value = 1
    mock_database.return_value = mock_db_instance

    result = cleanup_expired_transactions()

    assert result['status'] == 'success'
    assert result['deleted_count'] == 1
    assert result['deleted_ids'] == [1]
    mock_db_instance.query.assert_called_once()
    mock_db_instance.delete.assert_called_once()

def test_cleanup_expired_transactions_exception_handling(mock_database):
    # Setup: Simulate a database error
    mock_database.side_effect = Exception("Database connection error")

    result = cleanup_expired_transactions()

    assert result['status'] == 'error'
    assert 'Database connection error' in result['message']

def test_configure_transaction_cleanup_job():
    result = configure_transaction_cleanup_job()

    assert result['status'] == 'success'
    assert result['configuration']['interval_hours'] == 24
    assert result['configuration']['expiration_hours'] == 24
    assert result['configuration']['max_transactions_to_delete'] == 1000

def test_configure_transaction_cleanup_job_custom_parameters():
    result = configure_transaction_cleanup_job(
        interval_hours=12, 
        expiration_hours=6, 
        max_transactions_to_delete=500
    )

    assert result['status'] == 'success'
    assert result['configuration']['interval_hours'] == 12
    assert result['configuration']['expiration_hours'] == 6
    assert result['configuration']['max_transactions_to_delete'] == 500