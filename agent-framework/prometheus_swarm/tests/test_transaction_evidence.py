import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_evidence import Base, TransactionEvidence, validate_transaction_evidence

@pytest.fixture(scope='function')
def session():
    """
    Create a test database session for each test function
    """
    # Use in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_validate_transaction_evidence_success():
    """
    Test successful validation of transaction evidence
    """
    transaction_hash = 'test_hash_123'
    transaction_type = 'transfer'
    evidence_data = {
        'sender': 'user1',
        'recipient': 'user2',
        'amount': 100
    }

    assert validate_transaction_evidence(transaction_hash, transaction_type, evidence_data)

def test_validate_transaction_evidence_missing_hash():
    """
    Test validation fails when transaction hash is missing
    """
    with pytest.raises(ValueError, match="Transaction hash is required"):
        validate_transaction_evidence('', 'transfer', {'amount': 100})

def test_validate_transaction_evidence_missing_type():
    """
    Test validation fails when transaction type is missing
    """
    with pytest.raises(ValueError, match="Transaction type is required"):
        validate_transaction_evidence('test_hash', '', {'amount': 100})

def test_validate_transaction_evidence_invalid_data_type():
    """
    Test validation fails when evidence data is not a dictionary
    """
    with pytest.raises(ValueError, match="Evidence data must be a dictionary"):
        validate_transaction_evidence('test_hash', 'transfer', 'invalid_data')

def test_transaction_evidence_unique_constraint(session):
    """
    Test uniqueness constraint prevents duplicate transaction evidence
    """
    transaction_hash = 'duplicate_hash'
    transaction_type = 'transfer'
    evidence_data = {
        'sender': 'user1',
        'recipient': 'user2',
        'amount': 100
    }

    # First transaction evidence entry
    evidence1 = TransactionEvidence(
        transaction_hash=transaction_hash,
        transaction_type=transaction_type,
        evidence_data=evidence_data
    )
    session.add(evidence1)
    session.commit()

    # Try to add another entry with same transaction_hash and transaction_type
    evidence2 = TransactionEvidence(
        transaction_hash=transaction_hash,
        transaction_type=transaction_type,
        evidence_data=evidence_data
    )
    session.add(evidence2)

    with pytest.raises(Exception):  # SQLAlchemy will raise an IntegrityError
        session.commit()