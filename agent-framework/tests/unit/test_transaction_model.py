"""Unit tests for Transaction model."""

import pytest
from datetime import datetime
from sqlmodel import create_engine, SQLModel, Session
from prometheus_swarm.database.models import Transaction, TransactionStatus


@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


def test_create_transaction(engine):
    """Test creating a valid transaction."""
    with Session(engine) as session:
        transaction = Transaction(
            transaction_hash="test_hash_123",
            amount=100.50,
            currency="USD",
            sender="sender_addr",
            recipient="recipient_addr",
            status=TransactionStatus.PENDING,
            description="Test transaction"
        )
        session.add(transaction)
        session.commit()

        # Retrieve and verify
        db_transaction = session.get(Transaction, transaction.id)
        assert db_transaction is not None
        assert db_transaction.transaction_hash == "test_hash_123"
        assert db_transaction.amount == 100.50
        assert db_transaction.status == TransactionStatus.PENDING


def test_transaction_status_updates(engine):
    """Test updating transaction status."""
    with Session(engine) as session:
        transaction = Transaction(
            transaction_hash="test_hash_456",
            amount=200.75,
            currency="BTC",
            sender="sender_2",
            recipient="recipient_2",
            status=TransactionStatus.PENDING
        )
        session.add(transaction)
        session.commit()

        # Update status
        transaction.status = TransactionStatus.COMPLETED
        transaction.updated_at = datetime.utcnow()
        session.add(transaction)
        session.commit()

        # Retrieve and verify
        db_transaction = session.get(Transaction, transaction.id)
        assert db_transaction.status == TransactionStatus.COMPLETED
        assert db_transaction.updated_at is not None


def test_transaction_unique_hash(engine):
    """Test that transaction hash must be unique."""
    with Session(engine) as session:
        transaction1 = Transaction(
            transaction_hash="duplicate_hash",
            amount=50.0,
            currency="ETH",
            sender="sender_1",
            recipient="recipient_1",
            status=TransactionStatus.PENDING
        )
        session.add(transaction1)
        session.commit()

        # Attempt to create transaction with same hash (should raise error)
        with pytest.raises(Exception):
            transaction2 = Transaction(
                transaction_hash="duplicate_hash",
                amount=75.0,
                currency="ETH",
                sender="sender_2",
                recipient="recipient_2",
                status=TransactionStatus.PENDING
            )
            session.add(transaction2)
            session.commit()


def test_transaction_metadata(engine):
    """Test storing additional metadata."""
    with Session(engine) as session:
        transaction = Transaction(
            transaction_hash="metadata_hash",
            amount=300.25,
            currency="EUR",
            sender="sender_3",
            recipient="recipient_3",
            status=TransactionStatus.COMPLETED,
            transaction_metadata='{"fee": 5.0, "source": "payment_gateway"}'
        )
        session.add(transaction)
        session.commit()

        # Retrieve and verify
        db_transaction = session.get(Transaction, transaction.id)
        assert db_transaction.transaction_metadata == '{"fee": 5.0, "source": "payment_gateway"}'