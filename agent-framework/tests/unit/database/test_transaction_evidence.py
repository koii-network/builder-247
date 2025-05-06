"""Tests for Transaction Evidence Model."""

import pytest
from sqlmodel import create_engine, SQLModel, Session
from prometheus_swarm.database.transaction_evidence import TransactionEvidence
import uuid

@pytest.fixture(scope='function')
def session():
    """
    Create a new database session for each test function.
    """
    # Use an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:', echo=True)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_create_transaction_evidence(session):
    """
    Test creating a basic transaction evidence record.
    """
    evidence = TransactionEvidence(
        transaction_hash='abc123',
        transaction_type='transfer'
    )
    
    session.add(evidence)
    session.commit()
    
    assert evidence.id is not None
    assert evidence.transaction_hash == 'abc123'
    assert evidence.transaction_type == 'transfer'

def test_uniqueness_constraint(session):
    """
    Test that a duplicate transaction evidence record is not allowed.
    """
    # First record
    evidence1 = TransactionEvidence(
        transaction_hash='unique_hash',
        transaction_type='transfer'
    )
    session.add(evidence1)
    session.commit()
    
    # Try to add a duplicate record (same hash)
    with pytest.raises(Exception) as excinfo:
        evidence2 = TransactionEvidence(
            transaction_hash='unique_hash',
            transaction_type='another_transfer'
        )
        session.add(evidence2)
        session.commit()
    
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
        TransactionEvidence.validate_transaction_evidence(None, 'transfer')  # type: ignore
    
    with pytest.raises(ValueError, match="Transaction type must be a non-empty string"):
        TransactionEvidence.validate_transaction_evidence('hash', '')
    
    with pytest.raises(ValueError, match="Transaction type must be a non-empty string"):
        TransactionEvidence.validate_transaction_evidence('hash', None)  # type: ignore

def test_transaction_evidence_properties():
    """
    Test additional properties of TransactionEvidence.
    """
    evidence = TransactionEvidence(
        transaction_hash='test_hash',
        transaction_type='test_type'
    )
    
    assert evidence.transaction_hash == 'test_hash'
    assert evidence.transaction_type == 'test_type'
    assert evidence.created_at is not None
    assert evidence.updated_at is None
    assert isinstance(evidence.id, uuid.UUID)