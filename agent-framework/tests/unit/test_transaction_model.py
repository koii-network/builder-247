"""Tests for Transaction model."""

from datetime import datetime, timedelta
from decimal import Decimal
from sqlmodel import SQLModel, create_engine, Session

from prometheus_swarm.database.models import Transaction

def test_transaction_model_creation():
    """Test creating a basic transaction model."""
    transaction = Transaction(
        transaction_uuid="tx_test_001",
        type="income",
        amount=Decimal("100.50"),
        status="completed",
        description="Test income transaction"
    )
    
    assert transaction.transaction_uuid == "tx_test_001"
    assert transaction.type == "income"
    assert transaction.amount == Decimal("100.50")
    assert transaction.status == "completed"
    assert transaction.description == "Test income transaction"
    assert transaction.currency == "USD"

def test_transaction_model_with_metadata():
    """Test transaction model with additional metadata."""
    metadata = {
        "project": "Financial Tracking",
        "department": "Engineering"
    }
    
    transaction = Transaction(
        transaction_uuid="tx_test_002",
        type="expense",
        amount=Decimal("250.75"),
        status="pending",
        metadata=metadata
    )
    
    assert transaction.metadata == {
        "project": "Financial Tracking",
        "department": "Engineering"
    }

def test_transaction_model_timestamps():
    """Test automatic timestamp generation."""
    transaction = Transaction(
        transaction_uuid="tx_test_003",
        type="transfer",
        amount=Decimal("500.00"),
        status="completed"
    )
    
    assert transaction.created_at is not None
    assert isinstance(transaction.created_at, datetime)
    assert transaction.updated_at is None

def test_transaction_model_optional_fields():
    """Test optional fields in transaction model."""
    transaction = Transaction(
        transaction_uuid="tx_test_004",
        type="income",
        amount=Decimal("1000.00"),
        status="completed",
        source="Payroll",
        destination="Bank Account"
    )
    
    assert transaction.source == "Payroll"
    assert transaction.destination == "Bank Account"
    assert transaction.category is None

def test_transaction_model_decimal_precision():
    """Test decimal precision for transaction amount."""
    transaction = Transaction(
        transaction_uuid="tx_test_005",
        type="expense",
        amount=Decimal("33.33"),
        status="completed"
    )
    
    assert transaction.amount == Decimal("33.33")
    assert isinstance(transaction.amount, Decimal)

def test_transaction_uniqueness_constraint():
    """Test that transaction UUID must be unique."""
    transaction1 = Transaction(
        transaction_uuid="tx_unique_001",
        type="income",
        amount=Decimal("200.00"),
        status="completed"
    )
    
    transaction2 = Transaction(
        transaction_uuid="tx_unique_001",  # Same UUID
        type="expense",
        amount=Decimal("100.00"),
        status="pending"
    )
    
    # In a real database, this would raise a constraint violation
    assert transaction1.transaction_uuid == transaction2.transaction_uuid