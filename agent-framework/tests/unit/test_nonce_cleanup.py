import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from agent-framework.prometheus_swarm.database.models import Base, Nonce
from agent-framework.prometheus_swarm.utils.nonce_cleanup import cleanup_expired_nonces

@pytest.fixture
def db_session():
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()

def test_cleanup_expired_nonces(db_session: Session):
    # Create some nonces with different ages
    current_time = datetime.utcnow()
    
    # Fresh nonce (should not be deleted)
    fresh_nonce = Nonce(value='fresh', created_at=current_time)
    
    # Expired nonce (more than 24 hours old)
    expired_nonce = Nonce(value='expired', created_at=current_time - timedelta(hours=25))
    
    # Add nonces to the session
    db_session.add(fresh_nonce)
    db_session.add(expired_nonce)
    db_session.commit()

    # Run cleanup
    deleted_count = cleanup_expired_nonces(db_session)

    # Verify results
    assert deleted_count == 1

    # Check remaining nonces
    remaining_nonces = db_session.query(Nonce).all()
    assert len(remaining_nonces) == 1
    assert remaining_nonces[0].value == 'fresh'

def test_cleanup_invalid_max_age():
    # Create a mock session (not used in this test)
    mock_session = None

    # Test negative max_age_hours
    with pytest.raises(ValueError, match="Max age must be a positive number"):
        cleanup_expired_nonces(mock_session, max_age_hours=-1)

    # Test zero max_age_hours
    with pytest.raises(ValueError, match="Max age must be a positive number"):
        cleanup_expired_nonces(mock_session, max_age_hours=0)

def test_custom_max_age(db_session: Session):
    # Create some nonces with different ages
    current_time = datetime.utcnow()
    
    # Nonce 12 hours old (should not be deleted with 10-hour max age)
    mid_age_nonce = Nonce(value='mid_age', created_at=current_time - timedelta(hours=12))
    
    # Nonce 14 hours old (should be deleted with 10-hour max age)
    old_nonce = Nonce(value='old', created_at=current_time - timedelta(hours=14))
    
    # Add nonces to the session
    db_session.add(mid_age_nonce)
    db_session.add(old_nonce)
    db_session.commit()

    # Run cleanup with custom max age
    deleted_count = cleanup_expired_nonces(db_session, max_age_hours=10)

    # Verify results
    assert deleted_count == 1

    # Check remaining nonces
    remaining_nonces = db_session.query(Nonce).all()
    assert len(remaining_nonces) == 1
    assert remaining_nonces[0].value == 'mid_age'