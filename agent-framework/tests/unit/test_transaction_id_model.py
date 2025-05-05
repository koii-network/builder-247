import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.models import Base, TransactionID
import uuid

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

def test_transaction_id_creation(session):
    """Test creating a new TransactionID."""
    txn = TransactionID.create(source='test_source')
    session.add(txn)
    session.commit()
    
    assert txn.source == 'test_source'
    assert txn.transaction_uuid is not None
    assert isinstance(txn.created_at, datetime)
    assert len(str(txn.transaction_uuid)) == 36  # Standard UUID length

def test_transaction_id_with_metadata(session):
    """Test creating a TransactionID with metadata."""
    txn = TransactionID.create(
        source='complex_task', 
        metadata='{"priority": "high", "retry_count": 3}'
    )
    session.add(txn)
    session.commit()
    
    assert txn.source == 'complex_task'
    assert txn.metadata == '{"priority": "high", "retry_count": 3}'

def test_transaction_id_uniqueness(session):
    """Ensure each TransactionID has a unique UUID."""
    txn1 = TransactionID.create(source='source1')
    txn2 = TransactionID.create(source='source2')
    session.add_all([txn1, txn2])
    session.commit()
    
    assert txn1.transaction_uuid != txn2.transaction_uuid

def test_transaction_id_repr(session):
    """Test the string representation of TransactionID."""
    txn = TransactionID.create(source='test_source')
    repr_str = repr(txn)
    
    assert 'TransactionID' in repr_str
    assert txn.transaction_uuid in repr_str
    assert 'test_source' in repr_str

def test_transaction_id_creation_timestamp(session):
    """Verify the created_at timestamp is close to the current time."""
    txn = TransactionID.create(source='time_check')
    session.add(txn)
    session.commit()
    
    now = datetime.utcnow()
    assert abs(now - txn.created_at) < timedelta(seconds=1)

def test_transaction_id_mandatory_fields(session):
    """Ensure source is a mandatory field."""
    with pytest.raises(TypeError):
        TransactionID.create()  # Missing source

def test_multiple_transaction_ids(session):
    """Create multiple transaction IDs and verify their properties."""
    txns = [TransactionID.create(source=f'source_{i}') for i in range(5)]
    session.add_all(txns)
    session.commit()
    
    retrieved_txns = session.query(TransactionID).all()
    assert len(retrieved_txns) == 5
    assert len(set(txn.transaction_uuid for txn in retrieved_txns)) == 5