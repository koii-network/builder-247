import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_models import Base, TransactionID, create_transaction_id_table
from datetime import datetime, timedelta

@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    return create_engine('sqlite:///:memory:')

@pytest.fixture
def session(engine):
    """Create a database session for testing."""
    create_transaction_id_table(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_transaction_id_creation(session):
    """Test creating a basic TransactionID record."""
    tx_id = TransactionID(
        transaction_id='test-tx-001', 
        source='test_system', 
        status='pending'
    )
    session.add(tx_id)
    session.commit()

    # Retrieve and verify
    retrieved_tx = session.query(TransactionID).filter_by(transaction_id='test-tx-001').first()
    assert retrieved_tx is not None
    assert retrieved_tx.source == 'test_system'
    assert retrieved_tx.status == 'pending'
    assert not retrieved_tx.is_processed

def test_transaction_id_defaults(session):
    """Test default values for TransactionID."""
    tx_id = TransactionID(
        transaction_id='default-tx-001', 
        source='default_system'
    )
    session.add(tx_id)
    session.commit()

    retrieved_tx = session.query(TransactionID).filter_by(transaction_id='default-tx-001').first()
    assert retrieved_tx.status == 'pending'
    assert retrieved_tx.is_processed == False
    assert retrieved_tx.created_at is not None
    assert retrieved_tx.updated_at is not None

def test_transaction_id_metadata(session):
    """Test adding metadata to a TransactionID."""
    tx_id = TransactionID(
        transaction_id='metadata-tx-001', 
        source='metadata_system',
        transaction_metadata={
            'user_id': 123,
            'operation': 'create',
            'additional_info': {'key': 'value'}
        }
    )
    session.add(tx_id)
    session.commit()

    retrieved_tx = session.query(TransactionID).filter_by(transaction_id='metadata-tx-001').first()
    assert retrieved_tx.transaction_metadata['user_id'] == 123
    assert retrieved_tx.transaction_metadata['operation'] == 'create'

def test_transaction_id_unique_constraint(session):
    """Test that transaction IDs must be unique."""
    tx_id1 = TransactionID(
        transaction_id='unique-tx-001', 
        source='system1'
    )
    session.add(tx_id1)
    session.commit()

    # Attempt to add duplicate transaction ID should raise an error
    with pytest.raises(Exception):
        tx_id2 = TransactionID(
            transaction_id='unique-tx-001', 
            source='system2'
        )
        session.add(tx_id2)
        session.commit()

def test_transaction_id_repr(session):
    """Test the string representation of TransactionID."""
    tx_id = TransactionID(
        transaction_id='repr-tx-001', 
        source='repr_system', 
        status='completed'
    )
    
    repr_str = repr(tx_id)
    assert 'repr-tx-001' in repr_str
    assert 'repr_system' in repr_str
    assert 'completed' in repr_str