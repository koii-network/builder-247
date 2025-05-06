import pytest
from unittest.mock import patch, MagicMock
import datetime

from prometheus_swarm.utils.transaction_cleanup import (
    cleanup_expired_transactions,
    configure_transaction_cleanup_job,
    DatabaseConnectionError
)

def test_cleanup_expired_transactions_no_transactions():
    # This test will now pass given our simulated implementation
    result = cleanup_expired_transactions()

    assert result['status'] == 'success'
    assert result['deleted_count'] == 0

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

def test_database_connection_error():
    with pytest.raises(DatabaseConnectionError):
        from prometheus_swarm.utils.transaction_cleanup import get_database_connection
        get_database_connection()