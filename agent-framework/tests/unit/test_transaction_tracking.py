"""Unit tests for TransactionTracking model."""

import pytest
import json
from datetime import datetime, timedelta
from sqlmodel import SQLModel, create_engine, Session
from prometheus_swarm.database.models import TransactionTracking


@pytest.fixture
def session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_transaction(session):
    """Test creating a new transaction."""
    transaction = TransactionTracking.create_transaction(
        transaction_id="test_tx_1",
        source="test_source",
        metadata={"key": "value"}
    )
    session.add(transaction)
    session.commit()

    # Verify transaction was saved
    saved_tx = session.get(TransactionTracking, transaction.id)
    assert saved_tx is not None
    assert saved_tx.transaction_id == "test_tx_1"
    assert saved_tx.status == "pending"
    assert saved_tx.source == "test_source"
    assert json.loads(saved_tx.metadata) == {"key": "value"}


def test_update_transaction_status(session):
    """Test updating a transaction's status."""
    transaction = TransactionTracking.create_transaction(
        transaction_id="test_tx_2",
    )
    session.add(transaction)
    session.commit()

    # Track original timestamps
    original_created_at = transaction.created_at
    original_updated_at = transaction.updated_at

    # Simulate small time passage
    transaction.update_status("completed")
    session.commit()

    # Verify status and timestamps
    saved_tx = session.get(TransactionTracking, transaction.id)
    assert saved_tx.status == "completed"
    assert saved_tx.created_at == original_created_at
    assert saved_tx.updated_at > original_updated_at


def test_unique_transaction_id_constraint(session):
    """Test that transaction IDs are unique."""
    transaction1 = TransactionTracking.create_transaction(
        transaction_id="unique_tx_1"
    )
    session.add(transaction1)
    session.commit()

    # Attempt to create another transaction with the same ID
    with pytest.raises(Exception):  # SQLAlchemy will raise an IntegrityError
        transaction2 = TransactionTracking.create_transaction(
            transaction_id="unique_tx_1"
        )
        session.add(transaction2)
        session.commit()


def test_metadata_parsing(session):
    """Test metadata parsing and retrieval."""
    transaction = TransactionTracking.create_transaction(
        transaction_id="test_tx_3",
        metadata={"user_id": 123, "details": {"type": "payment"}}
    )
    session.add(transaction)
    session.commit()

    saved_tx = session.get(TransactionTracking, transaction.id)
    parsed_metadata = saved_tx.get_metadata()
    
    assert parsed_metadata == {"user_id": 123, "details": {"type": "payment"}}