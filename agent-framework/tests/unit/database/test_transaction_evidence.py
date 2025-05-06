import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.database import Base
from prometheus_swarm.database.transaction_evidence import TransactionEvidence
import uuid

@pytest.fixture(scope='function')
def db_session():
    """
    Create a new database session for each test function.
    """
    # Use an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

def test_create_transaction_evidence(db_session):
    """
    Test creating a basic transaction evidence record.
    """
    evidence = TransactionEvidence(
        transaction_hash='abc123',
        transaction_type='transfer'
    )
    
    db_session.add(evidence)
    db_session.commit()
    
    assert evidence.id is not None
    assert evidence.transaction_hash == 'abc123'
    assert evidence.transaction_type == 'transfer'

def test_uniqueness_constraint(db_session):
    """
    Test that a duplicate transaction evidence record is not allowed.
    """
    # First record
    evidence1 = TransactionEvidence(
        transaction_hash='unique_hash',
        transaction_type='transfer'
    )
    db_session.add(evidence1)
    db_session.commit()
    
    # Try to add a duplicate record (same hash and type)
    with pytest.raises(Exception) as excinfo:
        evidence2 = TransactionEvidence(
            transaction_hash='unique_hash',
            transaction_type='transfer'
        )
        db_session.add(evidence2)
        db_session.commit()
    
    assert 'UNIQUE constraint' in str(excinfo.value)

def test_validate_transaction_evidence():
    """
    Test validation method for transaction evidence.
    """
    # Valid inputs
    TransactionEvidence.validate_transaction_evidence('valid_hash', 'transfer')
    
    # Test invalid inputs
    with pytest.raises(ValueError, match="Transaction hash must be a non-empty string"):
        TransactionEvidence.validate_transaction_evidence('', 'transfer')
    
    with pytest.raises(ValueError, match="Transaction hash must be a non-empty string"):
        TransactionEvidence.validate_transaction_evidence(None, 'transfer')
    
    with pytest.raises(ValueError, match="Transaction type must be a non-empty string"):
        TransactionEvidence.validate_transaction_evidence('hash', '')
    
    with pytest.raises(ValueError, match="Transaction type must be a non-empty string"):
        TransactionEvidence.validate_transaction_evidence('hash', None)

def test_transaction_evidence_repr():
    """
    Test the string representation of TransactionEvidence.
    """
    evidence = TransactionEvidence(
        id=uuid.uuid4(),
        transaction_hash='test_hash',
        transaction_type='test_type'
    )
    
    repr_str = repr(evidence)
    assert 'TransactionEvidence' in repr_str
    assert 'test_hash' in repr_str
    assert 'test_type' in repr_str