"""Unit tests for Transaction tracking model."""

import pytest
from uuid import UUID
from datetime import datetime, timedelta
from sqlmodel import SQLModel, create_engine, Session

from prometheus_swarm.database.models import Transaction
from prometheus_swarm.database.config import get_sqlite_db_url


def test_transaction_creation():
    """Test creating a valid transaction."""
    transaction = Transaction(
        source="user1",
        destination="user2",
        amount=100.50,
        currency="USD",
        transaction_type="transfer"
    )

    assert isinstance(transaction.id, str)
    assert UUID(transaction.id)  # Validate UUID format
    assert transaction.source == "user1"
    assert transaction.destination == "user2"
    assert transaction.amount == 100.50
    assert transaction.currency == "USD"
    assert transaction.transaction_type == "transfer"
    assert transaction.status == "pending"
    assert isinstance(transaction.created_at, datetime)
    assert isinstance(transaction.updated_at, datetime)


def test_transaction_status_validation():
    """Test transaction status validation."""
    valid_statuses = ["pending", "completed", "failed", "refunded", "cancelled"]
    for status in valid_statuses:
        transaction = Transaction(
            source="user1",
            destination="user2",
            amount=50.00,
            currency="USD",
            transaction_type="transfer",
            status=status
        )
        assert transaction.status == status

    with pytest.raises(ValueError):
        Transaction(
            source="user1",
            destination="user2",
            amount=50.00,
            currency="USD",
            transaction_type="transfer",
            status="invalid_status"
        )


def test_transaction_database_integration():
    """Test Transaction model database integration."""
    engine = create_engine(get_sqlite_db_url())
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        transaction = Transaction(
            source="user1",
            destination="user2",
            amount=200.75,
            currency="USD",
            transaction_type="payment"
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        # Retrieve transaction
        db_transaction = session.get(Transaction, transaction.id)
        assert db_transaction is not None
        assert db_transaction.amount == 200.75

        # Optional metadata
        transaction.metadata = '{"ref_code": "ABC123"}'
        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        assert transaction.metadata == '{"ref_code": "ABC123"}'


def test_transaction_timestamps():
    """Test transaction timestamp behavior."""
    transaction = Transaction(
        source="user1",
        destination="user2",
        amount=75.25,
        currency="USD",
        transaction_type="withdrawal"
    )

    initial_created_at = transaction.created_at
    initial_updated_at = transaction.updated_at

    # Simulate a small time pass
    import time
    time.sleep(0.1)

    transaction.status = "completed"

    assert transaction.created_at == initial_created_at
    assert transaction.updated_at > initial_updated_at