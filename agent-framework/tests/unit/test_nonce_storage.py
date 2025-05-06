import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.nonce_models import Base, Nonce
from prometheus_swarm.database.nonce_storage import SqlAlchemyNonceStorage

@pytest.fixture(scope='function')
def session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def nonce_storage(session):
    """Create a nonce storage instance with the test session."""
    return SqlAlchemyNonceStorage(session)

def test_create_nonce(nonce_storage):
    """Test creating a new nonce token."""
    token = nonce_storage.create_nonce(purpose='test')
    assert token is not None
    assert len(token) > 0

def test_validate_nonce(session, nonce_storage):
    """Test validating a nonce token."""
    # Create a nonce
    token = nonce_storage.create_nonce(purpose='test')
    
    # Validate the nonce
    assert nonce_storage.validate_nonce(token, purpose='test') is True
    
    # Check that a different purpose fails
    assert nonce_storage.validate_nonce(token, purpose='wrong') is False

def test_consume_nonce(session, nonce_storage):
    """Test consuming a nonce token."""
    # Create a nonce
    token = nonce_storage.create_nonce(purpose='test')
    
    # Consume the nonce
    assert nonce_storage.consume_nonce(token) is True
    
    # Attempt to consume again should fail
    assert nonce_storage.consume_nonce(token) is False
    
    # Validate should also fail after consumption
    assert nonce_storage.validate_nonce(token) is False

def test_nonce_expiration(session, nonce_storage):
    """Test nonce expiration."""
    # Create a short-lived nonce (1 second validity)
    token = nonce_storage.create_nonce(validity_minutes=0.017)  # ~1 second
    
    # Validate should initially pass
    assert nonce_storage.validate_nonce(token) is True
    
    # Wait for the nonce to expire
    import time
    time.sleep(2)
    
    # Validate should now fail
    assert nonce_storage.validate_nonce(token) is False

def test_cleanup_expired_nonces(session, nonce_storage):
    """Test cleaning up expired nonces."""
    # Create some nonces at different times
    tokens = [
        nonce_storage.create_nonce(purpose='expired1', validity_minutes=0.01),
        nonce_storage.create_nonce(purpose='expired2', validity_minutes=0.01),
        nonce_storage.create_nonce(purpose='valid', validity_minutes=10)
    ]
    
    # Wait for expiration
    import time
    time.sleep(2)
    
    # Perform cleanup
    deleted_count = nonce_storage.cleanup_expired_nonces()
    
    # Check cleanup results
    assert deleted_count == 2

    # Verify remaining nonce is valid
    remaining_nonces = session.query(Nonce).all()
    assert len(remaining_nonces) == 1
    assert remaining_nonces[0].purpose == 'valid'