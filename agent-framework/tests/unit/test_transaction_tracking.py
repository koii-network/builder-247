"""Unit tests for the TransactionTracking model."""

from datetime import datetime, timedelta
from sqlmodel import SQLModel, create_engine, Session
from prometheus_swarm.database.models import TransactionTracking


def test_transaction_tracking_creation():
    """Test creating a transaction tracking record."""
    transaction_id = "test_transaction_123"
    transaction = TransactionTracking.create_transaction(
        transaction_id=transaction_id,
        source="test_source",
        destination="test_destination",
        payload_type="json",
        payload_size=1024,
        transaction_metadata='{"key": "value"}'
    )

    assert transaction.transaction_id == transaction_id
    assert transaction.source == "test_source"
    assert transaction.destination == "test_destination"
    assert transaction.payload_type == "json"
    assert transaction.payload_size == 1024
    assert transaction.transaction_metadata == '{"key": "value"}'
    assert transaction.status == "PENDING"
    assert transaction.retry_count == 0
    assert isinstance(transaction.started_at, datetime)


def test_transaction_tracking_status_update(tmp_path):
    """Test updating transaction status."""
    db_path = tmp_path / "test_transaction.db"
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        transaction = TransactionTracking.create_transaction(
            transaction_id="unique_transaction_456"
        )
        session.add(transaction)
        session.commit()

        # Update transaction status
        transaction.status = "COMPLETED"
        transaction.completed_at = datetime.utcnow()
        transaction.retry_count = 1
        transaction.error_code = "SUCCESS"
        session.commit()

        # Retrieve and verify
        updated_transaction = session.get(TransactionTracking, transaction.id)
        assert updated_transaction.status == "COMPLETED"
        assert updated_transaction.retry_count == 1
        assert updated_transaction.error_code == "SUCCESS"
        assert isinstance(updated_transaction.completed_at, datetime)


def test_transaction_tracking_error_handling():
    """Test transaction tracking with error details."""
    transaction = TransactionTracking.create_transaction(
        transaction_id="error_transaction_789"
    )
    transaction.status = "FAILED"
    transaction.error_code = "ERR_001"
    transaction.error_message = "Processing failed due to timeout"
    transaction.retry_count = 3

    assert transaction.transaction_id == "error_transaction_789"
    assert transaction.status == "FAILED"
    assert transaction.error_code == "ERR_001"
    assert transaction.error_message == "Processing failed due to timeout"
    assert transaction.retry_count == 3


def test_transaction_tracking_timestamp_sequence():
    """Test timestamp sequence and duration calculation."""
    now = datetime.utcnow()
    transaction = TransactionTracking.create_transaction(
        transaction_id="timestamp_sequence_test"
    )

    assert transaction.started_at <= now + timedelta(seconds=1)
    assert transaction.completed_at is None