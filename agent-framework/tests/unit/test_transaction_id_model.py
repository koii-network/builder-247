"""Unit tests for TransactionID model."""

from datetime import datetime, timedelta
from uuid import UUID
from sqlmodel import SQLModel, create_engine, Session
from prometheus_swarm.database.models import TransactionID
import pytest


def test_transaction_id_creation():
    """Test basic creation of a TransactionID."""
    transaction = TransactionID(
        namespace="test_workflow",
        context="unit_test",
        description="Test transaction creation"
    )

    assert transaction.namespace == "test_workflow"
    assert transaction.context == "unit_test"
    assert transaction.status == "pending"
    assert transaction.description == "Test transaction creation"

    # Validate UUID format
    assert is_valid_uuid(transaction.id)

    # Validate timestamps
    assert isinstance(transaction.created_at, datetime)
    assert isinstance(transaction.updated_at, datetime)
    assert transaction.created_at <= datetime.utcnow()
    assert transaction.updated_at <= datetime.utcnow()


def test_transaction_id_defaults():
    """Test that default values are correctly set."""
    transaction = TransactionID(namespace="test")

    assert transaction.namespace == "test"
    assert transaction.context is None
    assert transaction.status == "pending"
    assert transaction.description is None
    assert transaction.additional_metadata is None


def test_transaction_id_timestamps():
    """Test timestamp behaviors."""
    transaction = TransactionID(namespace="timestamp_test")
    initial_created_at = transaction.created_at
    initial_updated_at = transaction.updated_at

    # Simulate a small time passage
    transaction.updated_at = datetime.utcnow() + timedelta(seconds=1)

    assert transaction.created_at == initial_created_at
    assert transaction.updated_at > initial_updated_at


def is_valid_uuid(val):
    """Validate UUID string."""
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False


@pytest.mark.parametrize("status", ["pending", "in_progress", "completed", "failed"])
def test_transaction_id_status(status):
    """Test various transaction statuses."""
    transaction = TransactionID(
        namespace="status_test",
        status=status
    )
    assert transaction.status == status


def test_transaction_id_metadata():
    """Test storing additional metadata."""
    transaction = TransactionID(
        namespace="metadata_test",
        additional_metadata='{"key": "value", "count": 42}'
    )
    assert transaction.additional_metadata == '{"key": "value", "count": 42}'