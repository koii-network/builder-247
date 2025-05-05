import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.database import Base
from prometheus_swarm.database.transaction_id import TransactionID

@pytest.fixture
def db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(db_engine):
    """Create a database session for testing."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()

def test_create_transaction_id(db_session):
    """Test creating a new TransactionID record."""
    transaction = TransactionID.create(
        transaction_id='test_tx_123',
        context='test_context',
        status='pending',
        metadata='additional_info'
    )
    db_session.add(transaction)
    db_session.commit()

    # Retrieve the transaction
    stored_transaction = db_session.query(TransactionID).filter_by(transaction_id='test_tx_123').first()
    
    assert stored_transaction is not None
    assert stored_transaction.transaction_id == 'test_tx_123'
    assert stored_transaction.context == 'test_context'
    assert stored_transaction.status == 'pending'
    assert stored_transaction.metadata == 'additional_info'
    assert isinstance(stored_transaction.timestamp, datetime)

def test_update_transaction_status(db_session):
    """Test updating the status of a transaction."""
    transaction = TransactionID.create(
        transaction_id='test_tx_456',
        context='test_context'
    )
    db_session.add(transaction)
    db_session.commit()

    # Update transaction status
    transaction.update_status('completed')
    db_session.commit()

    # Retrieve the updated transaction
    stored_transaction = db_session.query(TransactionID).filter_by(transaction_id='test_tx_456').first()
    
    assert stored_transaction.status == 'completed'

def test_unique_transaction_id(db_session):
    """Test that transaction IDs must be unique."""
    transaction1 = TransactionID.create(
        transaction_id='unique_tx_id',
        context='context1'
    )
    db_session.add(transaction1)
    db_session.commit()

    # Attempt to add another transaction with the same ID should raise an error
    transaction2 = TransactionID.create(
        transaction_id='unique_tx_id',
        context='context2'
    )
    db_session.add(transaction2)
    
    with pytest.raises(Exception):
        db_session.commit()

def test_transaction_id_repr():
    """Test the string representation of a TransactionID."""
    transaction = TransactionID.create(
        transaction_id='repr_test_tx',
        context='test_context',
        status='pending'
    )
    
    # Since ID is not set until database insertion, we'll check the content
    repr_str = str(transaction)
    assert 'transaction_id' in repr_str
    assert 'context' in repr_str
    assert 'status' in repr_str
    assert 'repr_test_tx' in repr_str
    assert 'test_context' in repr_str
    assert 'pending' in repr_str