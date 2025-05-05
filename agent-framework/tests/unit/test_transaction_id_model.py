import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_id_models import Base, TransactionID

@pytest.fixture(scope='function')
def engine():
    """Create an in-memory SQLite database for testing"""
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope='function')
def session(engine):
    """Create a database session"""
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_transaction_id_creation(session):
    """Test creating a basic TransactionID"""
    transaction = TransactionID(
        transaction_id='unique_tx_123',
        source='github',
        metadata={'repo': 'test-repo', 'action': 'pull_request'}
    )
    session.add(transaction)
    session.commit()

    # Retrieve and verify
    retrieved_tx = session.query(TransactionID).filter_by(transaction_id='unique_tx_123').first()
    assert retrieved_tx is not None
    assert retrieved_tx.source == 'github'
    assert retrieved_tx.metadata == {'repo': 'test-repo', 'action': 'pull_request'}

def test_transaction_id_timestamps(session):
    """Test automatic timestamp handling"""
    transaction = TransactionID(
        transaction_id='time_tx_456',
        source='local'
    )
    session.add(transaction)
    session.commit()

    retrieved_tx = session.query(TransactionID).filter_by(transaction_id='time_tx_456').first()
    
    # Check creation timestamp
    assert retrieved_tx.created_at is not None
    assert isinstance(retrieved_tx.created_at, datetime)

    # Check update timestamp
    assert retrieved_tx.updated_at is not None
    assert isinstance(retrieved_tx.updated_at, datetime)
    assert retrieved_tx.created_at <= retrieved_tx.updated_at

def test_transaction_id_unique_constraint(session):
    """Test unique constraint on transaction_id"""
    transaction1 = TransactionID(
        transaction_id='duplicate_tx',
        source='github'
    )
    session.add(transaction1)
    session.commit()

    # Attempt to add duplicate transaction_id should raise an error
    with pytest.raises(Exception):
        transaction2 = TransactionID(
            transaction_id='duplicate_tx',
            source='local'
        )
        session.add(transaction2)
        session.commit()

def test_repr_method():
    """Test the __repr__ method"""
    transaction = TransactionID(
        transaction_id='repr_tx_789',
        source='external'
    )
    repr_str = repr(transaction)
    assert 'repr_tx_789' in repr_str
    assert 'external' in repr_str