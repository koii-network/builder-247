import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.nonce import Base, Nonce, NonceManager

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

def test_nonce_generation(session):
    """Test nonce generation creates a unique hash."""
    nonce1 = Nonce.generate()
    nonce2 = Nonce.generate()
    
    assert nonce1.value != nonce2.value
    assert len(nonce1.value) == 64  # SHA-256 hash length

def test_nonce_expiration(session):
    """Test nonce expiration mechanism."""
    # Create a nonce with very short expiration
    nonce = Nonce.generate(expiration_minutes=0)
    session.add(nonce)
    session.commit()
    
    # Simulate time passing
    nonce.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    session.commit()
    
    assert not nonce.is_valid()

def test_nonce_manager_create_and_validate(session):
    """Test NonceManager create and validate methods."""
    nonce_manager = NonceManager(session)
    
    # Create a nonce
    nonce_value = nonce_manager.create_nonce()
    
    # Validate the nonce
    assert nonce_manager.validate_nonce(nonce_value) is True
    
    # Nonce should be consumed, so second validation fails
    assert nonce_manager.validate_nonce(nonce_value) is False

def test_nonce_manager_invalid_nonce(session):
    """Test validation of an invalid/non-existent nonce."""
    nonce_manager = NonceManager(session)
    
    assert nonce_manager.validate_nonce('invalid_nonce') is False

def test_nonce_manager_expired_nonce_cleanup(session):
    """Test cleanup of expired nonces."""
    nonce_manager = NonceManager(session)
    
    # Create multiple nonces with different expiration times
    nonce1 = Nonce.generate(expiration_minutes=0)
    nonce2 = Nonce.generate(expiration_minutes=0)
    nonce3 = Nonce.generate(expiration_minutes=60)
    
    session.add_all([nonce1, nonce2, nonce3])
    session.commit()
    
    # Simulate time passing for first two nonces
    nonce1.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    nonce2.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    session.commit()
    
    # Cleanup expired nonces
    cleanup_count = nonce_manager.cleanup_expired_nonces()
    
    assert cleanup_count == 2
    
    # Check remaining nonces
    remaining_nonces = session.query(Nonce).all()
    assert len(remaining_nonces) == 1
    assert remaining_nonces[0] == nonce3

def test_nonce_context(session):
    """Test nonce creation with context."""
    context = "test_context"
    nonce_manager = NonceManager(session)
    
    nonce_value = nonce_manager.create_nonce(context=context)
    
    # Retrieve the nonce to check context
    nonce = session.query(Nonce).filter_by(value=nonce_value).first()
    
    assert nonce is not None
    assert nonce.context == context