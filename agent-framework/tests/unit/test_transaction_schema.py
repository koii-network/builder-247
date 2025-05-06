import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transactions import Transaction, TransactionStatus, initialize_transaction_table
from datetime import datetime, timedelta

@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing"""
    engine = create_engine('sqlite:///:memory:')
    initialize_transaction_table(engine)
    return engine

@pytest.fixture
def session(engine):
    """Create a database session"""
    Session = sessionmaker(bind=engine)
    return Session()

def test_create_transaction(session):
    """Test creating a basic transaction"""
    transaction = Transaction(
        transaction_type='transfer',
        amount=100.50,
        currency='USD',
        sender_id='user123',
        recipient_id='user456'
    )
    session.add(transaction)
    session.commit()

    # Verify transaction was saved
    saved_transaction = session.query(Transaction).first()
    assert saved_transaction is not None
    assert saved_transaction.amount == 100.50
    assert saved_transaction.status == TransactionStatus.PENDING

def test_transaction_timestamps(session):
    """Test automatic timestamp generation"""
    transaction = Transaction(
        transaction_type='payment',
        amount=50.00,
        currency='EUR',
        sender_id='user789',
        recipient_id='user012'
    )
    session.add(transaction)
    session.commit()

    # Check created_at and updated_at are set
    assert transaction.created_at is not None
    assert transaction.updated_at is not None
    assert transaction.created_at <= datetime.utcnow()
    assert transaction.updated_at <= datetime.utcnow()

def test_transaction_status_changes(session):
    """Test changing transaction status"""
    transaction = Transaction(
        transaction_type='refund',
        amount=25.75,
        currency='GBP',
        sender_id='user345',
        recipient_id='user678'
    )
    session.add(transaction)
    session.commit()

    # Change status and verify
    transaction.status = TransactionStatus.COMPLETED
    session.commit()

    updated_transaction = session.query(Transaction).first()
    assert updated_transaction.status == TransactionStatus.COMPLETED

def test_transaction_repr(session):
    """Test transaction string representation"""
    transaction = Transaction(
        transaction_type='purchase',
        amount=99.99,
        currency='USD',
        sender_id='user901',
        recipient_id='user234'
    )
    
    repr_str = repr(transaction)
    assert 'Transaction' in repr_str
    assert 'purchase' in repr_str
    assert '99.99' in repr_str