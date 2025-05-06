import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_evidence import Base, TransactionEvidence
import uuid

@pytest.fixture
def session():
    """Create a test database session."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_transaction_evidence_creation(session):
    """Test creating a valid transaction evidence record."""
    transaction_data = {
        'source': 'user1',
        'destination': 'user2',
        'amount': 100,
        'currency': 'USD'
    }
    
    transaction_hash = TransactionEvidence.generate_transaction_hash(transaction_data)
    
    evidence = TransactionEvidence(
        transaction_hash=transaction_hash,
        **transaction_data,
        extra_data={'note': 'test transaction'}
    )
    
    session.add(evidence)
    session.commit()
    
    assert evidence.id is not None
    assert evidence.transaction_hash == transaction_hash
    assert evidence.validate() is True
    assert evidence.extra_data == {'note': 'test transaction'}

def test_transaction_evidence_uniqueness(session):
    """Ensure transaction hash prevents duplicate entries."""
    transaction_data = {
        'source': 'user1',
        'destination': 'user2',
        'amount': 100,
        'currency': 'USD'
    }
    
    transaction_hash = TransactionEvidence.generate_transaction_hash(transaction_data)
    
    # First transaction
    evidence1 = TransactionEvidence(
        transaction_hash=transaction_hash,
        **transaction_data
    )
    session.add(evidence1)
    session.commit()
    
    # Attempt to create duplicate transaction
    with pytest.raises(Exception):
        evidence2 = TransactionEvidence(
            transaction_hash=transaction_hash,
            **transaction_data
        )
        session.add(evidence2)
        session.commit()

def test_transaction_evidence_validation():
    """Test validation logic for transaction evidence."""
    # Valid transaction
    valid_data = {
        'source': 'user1',
        'destination': 'user2',
        'amount': 100,
        'currency': 'USD'
    }
    
    transaction_hash = TransactionEvidence.generate_transaction_hash(valid_data)
    evidence = TransactionEvidence(
        transaction_hash=transaction_hash,
        **valid_data
    )
    
    assert evidence.validate() is True
    
    # Invalid transactions
    invalid_cases = [
        {'source': '', 'destination': 'user2', 'amount': 100, 'currency': 'USD'},
        {'source': 'user1', 'destination': '', 'amount': 100, 'currency': 'USD'},
        {'source': 'user1', 'destination': 'user2', 'amount': 0, 'currency': 'USD'},
        {'source': 'user1', 'destination': 'user2', 'amount': 100, 'currency': ''}
    ]
    
    for case in invalid_cases:
        transaction_hash = TransactionEvidence.generate_transaction_hash(case)
        evidence = TransactionEvidence(
            transaction_hash=transaction_hash,
            **case
        )
        assert evidence.validate() is False

def test_transaction_evidence_hash_generation():
    """Test hash generation is consistent and deterministic."""
    transaction_data1 = {
        'source': 'user1',
        'destination': 'user2',
        'amount': 100,
        'currency': 'USD'
    }
    
    transaction_data2 = {
        'source': 'user1',
        'destination': 'user2',
        'amount': 100,
        'currency': 'USD'
    }
    
    hash1 = TransactionEvidence.generate_transaction_hash(transaction_data1)
    hash2 = TransactionEvidence.generate_transaction_hash(transaction_data2)
    
    assert hash1 == hash2
    
    # Ensure different transactions generate different hashes
    transaction_data3 = {
        'source': 'user3',
        'destination': 'user4',
        'amount': 200,
        'currency': 'EUR'
    }
    
    hash3 = TransactionEvidence.generate_transaction_hash(transaction_data3)
    assert hash1 != hash3