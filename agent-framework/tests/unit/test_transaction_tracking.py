"""Tests for Transaction Tracking model."""

import pytest
from sqlmodel import SQLModel, create_engine, Session
from prometheus_swarm.database.models import TransactionTracking, TransactionStatus
from datetime import datetime, timedelta


@pytest.fixture
def test_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


def test_create_transaction_tracking(test_engine):
    """Test creating a transaction tracking record."""
    with Session(test_engine) as session:
        transaction = TransactionTracking(
            transaction_id="test_transaction_123",
            status=TransactionStatus.PENDING,
            description="Test transaction",
            workflow_name="test_workflow",
            initiator="test_user"
        )
        session.add(transaction)
        session.commit()

        # Retrieve and verify the transaction
        saved_transaction = session.get(TransactionTracking, transaction.id)
        assert saved_transaction is not None
        assert saved_transaction.transaction_id == "test_transaction_123"
        assert saved_transaction.status == TransactionStatus.PENDING
        assert saved_transaction.workflow_name == "test_workflow"
        assert saved_transaction.initiator == "test_user"


def test_transaction_status_update(test_engine):
    """Test updating transaction status."""
    with Session(test_engine) as session:
        transaction = TransactionTracking(
            transaction_id="test_transaction_456",
            status=TransactionStatus.PENDING
        )
        session.add(transaction)
        session.commit()

        # Update status
        transaction.status = TransactionStatus.PROCESSING
        session.commit()

        saved_transaction = session.get(TransactionTracking, transaction.id)
        assert saved_transaction.status == TransactionStatus.PROCESSING


def test_transaction_unique_id_constraint(test_engine):
    """Test that transaction_id is unique."""
    with Session(test_engine) as session:
        transaction1 = TransactionTracking(
            transaction_id="duplicate_transaction",
            status=TransactionStatus.PENDING
        )
        session.add(transaction1)
        session.commit()

        with pytest.raises(Exception):  # This will raise an SQLAlchemy IntegrityError
            transaction2 = TransactionTracking(
                transaction_id="duplicate_transaction",
                status=TransactionStatus.PENDING
            )
            session.add(transaction2)
            session.commit()


def test_transaction_default_values(test_engine):
    """Test default values for transaction tracking."""
    with Session(test_engine) as session:
        transaction = TransactionTracking(
            transaction_id="default_test_transaction"
        )
        session.add(transaction)
        session.commit()

        saved_transaction = session.get(TransactionTracking, transaction.id)
        assert saved_transaction.status == TransactionStatus.PENDING
        assert saved_transaction.created_at is not None
        assert saved_transaction.updated_at is not None


def test_transaction_extra_info(test_engine):
    """Test storing extra information in the transaction tracking."""
    with Session(test_engine) as session:
        transaction = TransactionTracking(
            transaction_id="extra_info_transaction",
            extra_info='{"key": "value", "additional_info": 42}'
        )
        session.add(transaction)
        session.commit()

        saved_transaction = session.get(TransactionTracking, transaction.id)
        assert saved_transaction.extra_info == '{"key": "value", "additional_info": 42}'