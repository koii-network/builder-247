"""Unit tests for TransactionTracking model."""

import json
from datetime import datetime, timedelta

import pytest
from sqlmodel import Session, create_engine, SQLModel

from prometheus_swarm.database.models import TransactionTracking
from prometheus_swarm.database.config import get_connection_string


@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    connection_string = "sqlite:///:memory:"
    engine = create_engine(connection_string)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a database session for each test."""
    with Session(engine) as session:
        yield session
        session.close()


def test_create_transaction(session):
    """Test creating a new transaction tracking entry."""
    transaction_id = "test-123"
    workflow_type = "task"
    source_module = "test_module"
    request_details = json.dumps({"key": "value"})

    transaction = TransactionTracking.create_transaction(
        transaction_id=transaction_id,
        workflow_type=workflow_type,
        source_module=source_module,
        request_details=request_details
    )

    session.add(transaction)
    session.commit()

    assert transaction.transaction_id == transaction_id
    assert transaction.workflow_type == workflow_type
    assert transaction.status == 'pending'
    assert transaction.source_module == source_module
    assert transaction.request_details == request_details
    assert transaction.created_at is not None
    assert transaction.updated_at is not None


def test_update_transaction_status(session):
    """Test updating the status of a transaction."""
    transaction = TransactionTracking.create_transaction(
        transaction_id="test-456",
        workflow_type="audit"
    )
    session.add(transaction)
    session.commit()

    # Capture the initial updated_at time
    initial_updated_at = transaction.updated_at

    # Wait a moment to ensure timestamp changes
    transaction.update_status('completed')
    session.commit()

    assert transaction.status == 'completed'
    assert transaction.updated_at > initial_updated_at


def test_update_transaction_with_error(session):
    """Test updating transaction status with an error message."""
    transaction = TransactionTracking.create_transaction(
        transaction_id="test-789",
        workflow_type="submission"
    )
    session.add(transaction)
    session.commit()

    error_msg = "Processing failed due to network error"
    transaction.update_status('failed', error_message=error_msg)
    session.commit()

    assert transaction.status == 'failed'
    assert transaction.error_message == error_msg


def test_unique_transaction_id(session):
    """Test that transaction IDs are unique."""
    transaction1 = TransactionTracking.create_transaction(
        transaction_id="unique-trans",
        workflow_type="task"
    )
    session.add(transaction1)
    session.commit()

    with pytest.raises(Exception) as exc_info:
        transaction2 = TransactionTracking.create_transaction(
            transaction_id="unique-trans",
            workflow_type="audit"
        )
        session.add(transaction2)
        session.commit()

    # Verify a unique constraint violation occurred
    assert "UNIQUE constraint" in str(exc_info.value)