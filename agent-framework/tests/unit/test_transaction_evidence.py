import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_evidence import Base, TransactionEvidence
import uuid

@pytest.fixture
def session():
    """
    Create an in-memory SQLite database for testing
    """
    # Use in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_transaction_evidence_creation(session):
    """
    Test creating a new transaction evidence record
    """
    # Create a unique transaction evidence
    evidence = TransactionEvidence(
        transaction_hash=str(uuid.uuid4()),
        transaction_source='test_source',
        evidence_type='test_type'
    )
    
    session.add(evidence)
    session.commit()
    
    # Verify the record was saved
    assert evidence.id is not None
    assert evidence.transaction_hash is not None
    assert evidence.transaction_source == 'test_source'
    assert evidence.evidence_type == 'test_type'

def test_transaction_evidence_unique_constraint(session):
    """
    Test that duplicate transactions are prevented
    """
    # First transaction
    first_hash = str(uuid.uuid4())
    first_evidence = TransactionEvidence(
        transaction_hash=first_hash,
        transaction_source='test_source',
        evidence_type='test_type'
    )
    
    session.add(first_evidence)
    session.commit()
    
    # Attempt to create duplicate transaction
    with pytest.raises(Exception):  # SQLAlchemy will raise an IntegrityError
        duplicate_evidence = TransactionEvidence(
            transaction_hash=first_hash,
            transaction_source='test_source',
            evidence_type='test_type'
        )
        session.add(duplicate_evidence)
        session.commit()

def test_transaction_evidence_different_types_allowed(session):
    """
    Test that different evidence types can use the same transaction hash
    """
    unique_hash = str(uuid.uuid4())
    
    # First evidence type
    first_evidence = TransactionEvidence(
        transaction_hash=unique_hash,
        transaction_source='test_source',
        evidence_type='type_1'
    )
    
    # Second evidence type with same hash
    second_evidence = TransactionEvidence(
        transaction_hash=unique_hash,
        transaction_source='test_source',
        evidence_type='type_2'
    )
    
    session.add(first_evidence)
    session.add(second_evidence)
    session.commit()
    
    # Verify both records were saved
    assert first_evidence.id is not None
    assert second_evidence.id is not None

def test_transaction_evidence_repr():
    """
    Test the string representation of TransactionEvidence
    """
    evidence = TransactionEvidence(
        transaction_hash='test_hash',
        transaction_source='test_source',
        evidence_type='test_type'
    )
    
    repr_str = repr(evidence)
    assert 'TransactionEvidence' in repr_str
    assert 'test_hash' in repr_str
    assert 'test_source' in repr_str
    assert 'test_type' in repr_str