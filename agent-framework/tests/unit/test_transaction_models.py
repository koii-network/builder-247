import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_models import (
    Base, Transaction, TransactionStatus, create_transaction_tables
)
from datetime import datetime, timedelta

@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    return create_engine('sqlite:///:memory:')

@pytest.fixture
def session(engine):
    """Create a database session for testing."""
    create_transaction_tables(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_transaction_creation(session):
    """Test creating a basic transaction."""
    transaction = Transaction(
        transaction_type='deposit',
        amount=100.00,
        currency='USD',
        status=TransactionStatus.PENDING,
        description='Test deposit'
    )
    session.add(transaction)
    session.commit()
    
    # Verify transaction was saved
    saved_transaction = session.query(Transaction).first()
    assert saved_transaction is not None
    assert saved_transaction.transaction_type == 'deposit'
    assert saved_transaction.amount == 100.00
    assert saved_transaction.currency == 'USD'
    assert saved_transaction.status == TransactionStatus.PENDING

def test_transaction_timestamp(session):
    """Test that timestamp is automatically set."""
    transaction = Transaction(
        transaction_type='withdrawal',
        amount=50.00,
        currency='USD'
    )
    session.add(transaction)
    session.commit()
    
    # Check timestamp is recent
    assert transaction.timestamp is not None
    assert transaction.timestamp <= datetime.utcnow()
    assert transaction.timestamp > datetime.utcnow() - timedelta(seconds=5)

def test_transaction_status_enum():
    """Test transaction status enum."""
    statuses = [
        TransactionStatus.PENDING,
        TransactionStatus.COMPLETED,
        TransactionStatus.FAILED,
        TransactionStatus.CANCELLED
    ]
    
    for status in statuses:
        transaction = Transaction(
            transaction_type='transfer',
            amount=75.00,
            currency='EUR',
            status=status
        )
        assert transaction.status == status

def test_transaction_repr():
    """Test string representation of transaction."""
    transaction = Transaction(
        transaction_type='payment',
        amount=200.00,
        currency='USD',
        status=TransactionStatus.COMPLETED
    )
    
    repr_str = repr(transaction)
    assert 'Transaction' in repr_str
    assert 'payment' in repr_str
    assert '200.0' in repr_str
    assert 'COMPLETED' in repr_str

def test_transaction_reference_id(session):
    """Test unique reference ID."""
    transaction1 = Transaction(
        transaction_type='deposit',
        amount=100.00,
        currency='USD',
        reference_id='TX001'
    )
    session.add(transaction1)
    session.commit()
    
    # Attempt to create transaction with same reference ID should raise integrity error
    with pytest.raises(Exception):
        transaction2 = Transaction(
            transaction_type='withdrawal',
            amount=50.00,
            currency='USD',
            reference_id='TX001'
        )
        session.add(transaction2)
        session.commit()