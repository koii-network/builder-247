import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.models import Base, TransactionID
import uuid
from datetime import datetime, timedelta

@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    return create_engine('sqlite:///:memory:')

@pytest.fixture
def session(engine):
    """Create a database session for testing."""
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_transaction_id_creation(session):
    """Test creating a new transaction ID."""
    transaction = TransactionID()
    session.add(transaction)
    session.commit()

    assert transaction.transaction_uuid is not None
    assert len(transaction.transaction_uuid) > 0
    assert transaction.status == 'PENDING'
    assert transaction.is_completed is False
    assert isinstance(transaction.created_at, datetime)

def test_transaction_id_mark_completed(session):
    """Test marking a transaction as completed."""
    transaction = TransactionID()
    session.add(transaction)
    session.commit()

    transaction.mark_completed()
    session.commit()

    assert transaction.is_completed is True
    assert transaction.status == 'COMPLETED'

def test_transaction_id_update_status(session):
    """Test updating transaction status."""
    transaction = TransactionID()
    session.add(transaction)
    session.commit()

    transaction.update_status('PROCESSING')
    session.commit()

    assert transaction.status == 'PROCESSING'

def test_transaction_id_unique_constraint(session):
    """Test that transaction UUIDs are unique."""
    transaction1 = TransactionID()
    transaction2 = TransactionID()
    session.add(transaction1)
    session.add(transaction2)
    session.commit()

    assert transaction1.transaction_uuid != transaction2.transaction_uuid

def test_transaction_with_metadata(session):
    """Test creating a transaction with metadata."""
    metadata = '{"key": "value"}'
    transaction = TransactionID.create_transaction(
        status='STARTED', 
        metadata=metadata
    )
    session.add(transaction)
    session.commit()

    assert transaction.status == 'STARTED'
    assert transaction.metadata == metadata

def test_transaction_timestamps(session):
    """Test transaction timestamp tracking."""
    transaction = TransactionID()
    session.add(transaction)
    session.commit()

    original_created_at = transaction.created_at
    original_updated_at = transaction.updated_at

    # Simulate some time passing and updating
    transaction.update_status('PROCESSING')
    session.commit()

    assert transaction.created_at == original_created_at
    assert transaction.updated_at > original_updated_at