import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_models import Base, Transaction
from datetime import datetime, timedelta
import uuid

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

def test_transaction_id_is_uuid(session):
    """Verify transaction_id is a valid UUID"""
    transaction = Transaction()
    session.add(transaction)
    session.commit()

    assert transaction.transaction_id is not None
    assert isinstance(transaction.transaction_id, uuid.UUID)

def test_created_at_defaults_to_current_timestamp(session):
    """Check that created_at defaults to current timestamp"""
    transaction = Transaction()
    session.add(transaction)
    session.commit()

    assert transaction.created_at is not None
    assert isinstance(transaction.created_at, datetime)
    
    # Check timestamp is very close to current time (within 1 second)
    time_difference = datetime.utcnow() - transaction.created_at
    assert abs(time_difference.total_seconds()) < 1

def test_created_at_millisecond_precision(session):
    """Verify millisecond-level timestamp precision"""
    transaction = Transaction()
    session.add(transaction)
    session.commit()

    # Microseconds are stored, which is more precise than milliseconds
    assert transaction.created_at.microsecond != 0

def test_expiration_time_optional(session):
    """Test that expiration_time can be set or left as default"""
    # Transaction with default expiration
    transaction1 = Transaction()
    session.add(transaction1)

    # Transaction with custom expiration
    custom_expiration = datetime.utcnow() + timedelta(days=2)
    transaction2 = Transaction(expiration_time=custom_expiration)
    session.add(transaction2)

    session.commit()

    assert transaction1.expiration_time is not None
    assert transaction2.expiration_time == custom_expiration

def test_unique_transaction_id(session):
    """Verify unique constraint on transaction_id"""
    transaction_id = uuid.uuid4()
    
    transaction1 = Transaction(transaction_id=transaction_id)
    session.add(transaction1)
    session.commit()

    with pytest.raises(Exception):
        transaction2 = Transaction(transaction_id=transaction_id)
        session.add(transaction2)
        session.commit()