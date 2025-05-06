"""
Test suite for transaction expiration and cleanup functionality.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import Session

from prometheus_swarm.database.transaction_cleanup import TransactionExpirationMixin

Base = declarative_base()

class MockTransaction(Base, TransactionExpirationMixin):
    """
    Mock transaction model for testing expiration cleanup.
    """
    __tablename__ = 'mock_transactions'
    
    id = Column(Integer, primary_key=True)
    value = Column(Integer)

@pytest.fixture
def db_session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()

def test_set_expiration(db_session: Session):
    """Test setting expiration time for a transaction."""
    transaction = MockTransaction(value=42)
    transaction.set_expiration(hours=2)
    
    assert transaction.expires_at is not None
    assert isinstance(transaction.expires_at, datetime)
    assert transaction.expires_at > datetime.utcnow()

def test_cleanup_expired_transactions(db_session: Session):
    """Test cleanup of expired transactions."""
    # Create some transactions
    old_transaction = MockTransaction(value=1)
    recent_transaction = MockTransaction(value=2)
    
    # Set custom timestamps to simulate aging
    old_transaction.created_at = datetime.utcnow() - timedelta(hours=25)
    recent_transaction.created_at = datetime.utcnow() - timedelta(hours=10)
    
    # Add transactions to session
    db_session.add(old_transaction)
    db_session.add(recent_transaction)
    db_session.commit()
    
    # Perform cleanup
    expired = MockTransaction.cleanup_expired_transactions(
        db_session, 
        expiration_hours=24
    )
    
    # Verify results
    assert len(expired) == 1
    assert expired[0].value == 1
    
    # Check remaining transactions
    remaining_transactions = db_session.query(MockTransaction).all()
    assert len(remaining_transactions) == 1
    assert remaining_transactions[0].value == 2

def test_cleanup_with_explicit_expiration(db_session: Session):
    """Test cleanup of transactions with explicit expiration time."""
    # Create transactions with different expiration scenarios
    expired_transaction = MockTransaction(value=10)
    not_expired_transaction = MockTransaction(value=20)
    
    # Set explicit expiration times
    expired_transaction.set_expiration(hours=1)
    not_expired_transaction.set_expiration(hours=24)
    
    # Simulate time passage
    expired_transaction.expires_at = datetime.utcnow() - timedelta(hours=2)
    
    # Add transactions to session
    db_session.add(expired_transaction)
    db_session.add(not_expired_transaction)
    db_session.commit()
    
    # Perform cleanup
    expired = MockTransaction.cleanup_expired_transactions(
        db_session, 
        expiration_hours=24
    )
    
    # Verify results
    assert len(expired) == 1
    assert expired[0].value == 10
    
    # Check remaining transactions
    remaining_transactions = db_session.query(MockTransaction).all()
    assert len(remaining_transactions) == 1
    assert remaining_transactions[0].value == 20