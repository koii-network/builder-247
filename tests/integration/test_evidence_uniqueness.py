import pytest
from prometheus_swarm.database.models import Evidence
from prometheus_swarm.database.database import SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List

def test_evidence_uniqueness():
    """
    Integration test to verify evidence uniqueness across the system.
    
    This test ensures that:
    1. Duplicate evidence cannot be inserted
    2. Each evidence entry has a unique identifier
    3. Constraints prevent duplicate evidence submissions
    """
    # Create a test database session
    engine = create_engine('sqlite:///:memory:')
    TestingSessionLocal = sessionmaker(bind=engine)
    
    # Create tables
    Evidence.__table__.create(bind=engine)
    
    def create_evidence(session, content: str, type: str) -> Evidence:
        """Helper function to create evidence entries"""
        evidence = Evidence(content=content, type=type)
        session.add(evidence)
        session.commit()
        return evidence

    # Test 1: Basic uniqueness
    with TestingSessionLocal() as session:
        # First evidence submission should succeed
        evidence1 = create_evidence(session, "Test Content 1", "test_type")
        assert evidence1.id is not None
        
        # Attempt to insert identical evidence should fail
        with pytest.raises(Exception) as excinfo:
            create_evidence(session, "Test Content 1", "test_type")
        
        assert "unique constraint" in str(excinfo.value).lower()

def test_evidence_multiple_types():
    """
    Test that different types of evidence can have the same content
    """
    engine = create_engine('sqlite:///:memory:')
    TestingSessionLocal = sessionmaker(bind=engine)
    
    Evidence.__table__.create(bind=engine)
    
    with TestingSessionLocal() as session:
        # Create evidence with same content, different types
        evidence1 = Evidence(content="Shared Content", type="type1")
        evidence2 = Evidence(content="Shared Content", type="type2")
        
        session.add(evidence1)
        session.add(evidence2)
        session.commit()
        
        # Verify both evidences were saved
        saved_evidences = session.query(Evidence).filter_by(content="Shared Content").all()
        assert len(saved_evidences) == 2
        assert {e.type for e in saved_evidences} == {"type1", "type2"}

def test_evidence_content_validation():
    """
    Test validation of evidence content
    """
    engine = create_engine('sqlite:///:memory:')
    TestingSessionLocal = sessionmaker(bind=engine)
    
    Evidence.__table__.create(bind=engine)
    
    with TestingSessionLocal() as session:
        # Test empty content
        with pytest.raises(Exception) as excinfo:
            empty_evidence = Evidence(content="", type="test_type")
            session.add(empty_evidence)
            session.commit()
        
        assert "empty" in str(excinfo.value).lower()
        
        # Test very long content
        long_content = "a" * 10001  # Assuming a max length constraint
        with pytest.raises(Exception) as excinfo:
            long_evidence = Evidence(content=long_content, type="test_type")
            session.add(long_evidence)
            session.commit()
        
        assert "length" in str(excinfo.value).lower()