import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from prometheus_swarm.database.transaction_models import Base, Transaction, TransactionStatus

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

def test_create_transaction(session):
    """Test creating a basic transaction."""
    transaction = Transaction(
        transaction_id='TXN-001',
        source_account='source_acct_123',
        destination_account='dest_acct_456',
        amount=100.50,
        currency='USD',
        status=TransactionStatus.PENDING
    )
    session.add(transaction)
    session.commit()

    # Retrieve and verify the transaction
    retrieved_txn = session.query(Transaction).filter_by(transaction_id='TXN-001').first()
    assert retrieved_txn is not None
    assert retrieved_txn.amount == 100.50
    assert retrieved_txn.status == TransactionStatus.PENDING

def test_transaction_default_values(session):
    """Test default values for transaction."""
    transaction = Transaction(
        transaction_id='TXN-002',
        source_account='source_acct_789',
        destination_account='dest_acct_012',
        amount=50.25,
        currency='EUR'
    )
    session.add(transaction)
    session.commit()

    retrieved_txn = session.query(Transaction).filter_by(transaction_id='TXN-002').first()
    assert retrieved_txn.status == TransactionStatus.PENDING
    assert isinstance(retrieved_txn.timestamp, datetime)
    assert retrieved_txn.description is None
    assert retrieved_txn.category is None

def test_transaction_status_changes(session):
    """Test changing transaction statuses."""
    transaction = Transaction(
        transaction_id='TXN-003',
        source_account='source_acct_345',
        destination_account='dest_acct_678',
        amount=200.00,
        currency='GBP'
    )
    session.add(transaction)
    session.commit()

    # Update status
    transaction.status = TransactionStatus.COMPLETED
    session.commit()

    retrieved_txn = session.query(Transaction).filter_by(transaction_id='TXN-003').first()
    assert retrieved_txn.status == TransactionStatus.COMPLETED

def test_transaction_repr(session):
    """Test the string representation of a transaction."""
    transaction = Transaction(
        transaction_id='TXN-004',
        source_account='source_acct_901',
        destination_account='dest_acct_234',
        amount=75.75,
        currency='CAD'
    )
    session.add(transaction)
    session.commit()

    repr_str = repr(transaction)
    assert 'Transaction' in repr_str
    assert 'TXN-004' in repr_str
    assert '75.75' in repr_str

def test_unique_transaction_id(session):
    """Test that transaction_id must be unique."""
    transaction1 = Transaction(
        transaction_id='TXN-DUPLICATE',
        source_account='source_acct_111',
        destination_account='dest_acct_222',
        amount=500.00,
        currency='USD'
    )
    session.add(transaction1)
    session.commit()

    # Attempt to add another transaction with same transaction_id should raise an error
    with pytest.raises(Exception):
        transaction2 = Transaction(
            transaction_id='TXN-DUPLICATE',
            source_account='source_acct_333',
            destination_account='dest_acct_444',
            amount=600.00,
            currency='USD'
        )
        session.add(transaction2)
        session.commit()