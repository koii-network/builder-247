"""Test suite for Transaction model."""

import uuid
from datetime import datetime, timedelta
from sqlmodel import SQLModel, create_engine, Session
from prometheus_swarm.database.models import Transaction, TransactionStatus


def test_transaction_model_creation():
    """Test creating a Transaction model instance."""
    # Create a transaction with all details
    transaction = Transaction(
        transaction_uuid=str(uuid.uuid4()),
        user_id="user123",
        transaction_type="purchase",
        description="Test transaction",
        status=TransactionStatus.PENDING,
        details={"product": "test_item", "quantity": 1},
        source_system="test_system"
    )

    assert transaction.transaction_type == "purchase"
    assert transaction.status == TransactionStatus.PENDING
    assert transaction.user_id == "user123"
    assert transaction.details == {"product": "test_item", "quantity": 1}
    assert transaction.source_system == "test_system"


def test_transaction_timestamps():
    """Test creation and updated timestamps."""
    transaction = Transaction(
        transaction_uuid=str(uuid.uuid4()),
        transaction_type="sale"
    )

    assert transaction.created_at is not None
    assert transaction.updated_at is not None
    assert isinstance(transaction.created_at, datetime)
    assert transaction.created_at <= datetime.utcnow()


def test_transaction_status_changes():
    """Test changing transaction status."""
    transaction = Transaction(
        transaction_uuid=str(uuid.uuid4()),
        transaction_type="transfer",
        status=TransactionStatus.PENDING
    )

    transaction.status = TransactionStatus.PROCESSING
    assert transaction.status == TransactionStatus.PROCESSING

    transaction.status = TransactionStatus.COMPLETED
    assert transaction.status == TransactionStatus.COMPLETED


def test_transaction_details_and_error_handling():
    """Test transaction details and error handling."""
    transaction = Transaction(
        transaction_uuid=str(uuid.uuid4()),
        transaction_type="refund",
        status=TransactionStatus.FAILED,
        error_message="Insufficient funds",
        stack_trace="Some detailed error trace"
    )

    assert transaction.status == TransactionStatus.FAILED
    assert transaction.error_message == "Insufficient funds"
    assert transaction.stack_trace == "Some detailed error trace"


def test_transaction_unique_uuid():
    """Test transaction UUID uniqueness."""
    uuid1 = str(uuid.uuid4())
    uuid2 = str(uuid.uuid4())

    transaction1 = Transaction(
        transaction_uuid=uuid1,
        transaction_type="test1"
    )

    transaction2 = Transaction(
        transaction_uuid=uuid2,
        transaction_type="test2"
    )

    assert transaction1.transaction_uuid != transaction2.transaction_uuid