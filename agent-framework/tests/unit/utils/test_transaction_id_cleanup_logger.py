import os
import logging
import tempfile
import pytest
from prometheus_swarm.utils.transaction_id_cleanup_logger import TransactionIdCleanupLogger

def test_logger_initialization():
    """Test logger initialization and basic functionality."""
    logger = TransactionIdCleanupLogger()
    assert logger.logger.level == logging.INFO
    assert len(logger.logger.handlers) == 2  # File and console handlers

def test_custom_log_level():
    """Test initializing logger with a custom log level."""
    logger = TransactionIdCleanupLogger(log_level=logging.DEBUG)
    assert logger.logger.level == logging.DEBUG

def test_log_directory_creation():
    """Verify log directory is created if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = TransactionIdCleanupLogger(log_dir=os.path.join(tmpdir, 'logs'))
        log_dir = os.path.join(tmpdir, 'logs', 'transaction_cleanup')
        assert os.path.exists(log_dir)

def test_log_methods(caplog):
    """Test logging methods capture correct information."""
    logger = TransactionIdCleanupLogger()
    transaction_id = 'test_tx_123'

    # Test log_cleanup_start
    logger.log_cleanup_start(transaction_id)
    assert f"Starting cleanup for transaction ID: {transaction_id}" in caplog.text

    # Reset caplog
    caplog.clear()

    # Test log_cleanup_success
    logger.log_cleanup_success(transaction_id, num_records_deleted=5, cleanup_duration=0.123)
    assert f"Cleanup successful for transaction ID: {transaction_id}" in caplog.text
    assert "Records deleted: 5" in caplog.text
    assert "Duration: 0.1230 seconds" in caplog.text

    # Reset caplog
    caplog.clear()

    # Test log_cleanup_error
    error_msg = "Database connection failed"
    logger.log_cleanup_error(transaction_id, error_msg)
    assert f"Cleanup failed for transaction ID: {transaction_id}" in caplog.text
    assert "Error: Database connection failed" in caplog.text

    # Reset caplog
    caplog.clear()

    # Test log_cleanup_skipped
    skip_reason = "Transaction already completed"
    logger.log_cleanup_skipped(transaction_id, skip_reason)
    assert f"Cleanup skipped for transaction ID: {transaction_id}" in caplog.text
    assert "Reason: Transaction already completed" in caplog.text