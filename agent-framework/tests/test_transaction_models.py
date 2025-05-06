import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_models import Base, Transaction, User, TransactionType, TransactionStatus
from datetime import datetime, timedelta

@pytest.fixture(scope='function')
def engine():
    """Create an in-memory SQLite database for testing"""
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope='function')
def session(engine):
    """Create a database session for testing"""
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_transaction(session):
    """Test creating a basic transaction"""
    user = User(username='testuser')
    session.add(user)
    session.commit()

    transaction = Transaction(
        user_id=user.id,
        amount=100.50,
        transaction_type=TransactionType.DEPOSIT,
        status=TransactionStatus.COMPLETED
    )
    session.add(transaction)
    session.commit()

    assert transaction.id is not None
    assert transaction.amount == 100.50
    assert transaction.transaction_type == TransactionType.DEPOSIT
    assert transaction.status == TransactionStatus.COMPLETED

def test_transaction_timestamps(session):
    """Test that timestamps are automatically set"""
    user = User(username='timestampuser')
    session.add(user)
    session.commit()

    transaction = Transaction(
        user_id=user.id,
        amount=50.0,
        transaction_type=TransactionType.WITHDRAWAL
    )
    session.add(transaction)
    session.commit()

    assert transaction.created_at is not None
    assert transaction.updated_at is not None
    assert isinstance(transaction.created_at, datetime)

def test_transaction_user_relationship(session):
    """Test the relationship between User and Transaction"""
    user = User(username='relationshipuser')
    session.add(user)
    
    transaction1 = Transaction(
        user_id=user.id,
        amount=200.0,
        transaction_type=TransactionType.TRANSFER
    )
    transaction2 = Transaction(
        user_id=user.id,
        amount=75.0,
        transaction_type=TransactionType.REWARD
    )
    session.add(transaction1)
    session.add(transaction2)
    session.commit()

    assert len(user.transactions) == 2
    assert transaction1 in user.transactions
    assert transaction2 in user.transactions

def test_transaction_status_validation(session):
    """Test different transaction statuses"""
    user = User(username='statususer')
    session.add(user)
    session.commit()

    statuses = [
        TransactionStatus.PENDING,
        TransactionStatus.COMPLETED,
        TransactionStatus.FAILED,
        TransactionStatus.CANCELLED
    ]

    for status in statuses:
        transaction = Transaction(
            user_id=user.id,
            amount=100.0,
            transaction_type=TransactionType.DEPOSIT,
            status=status
        )
        session.add(transaction)
    
    session.commit()

def test_transaction_optional_fields(session):
    """Test optional transaction fields"""
    user = User(username='optionaluser')
    session.add(user)
    session.commit()

    transaction = Transaction(
        user_id=user.id,
        amount=500.0,
        transaction_type=TransactionType.WITHDRAWAL,
        description="Monthly maintenance fee",
        external_reference="MAINT-2023-001"
    )
    session.add(transaction)
    session.commit()

    assert transaction.description == "Monthly maintenance fee"
    assert transaction.external_reference == "MAINT-2023-001"