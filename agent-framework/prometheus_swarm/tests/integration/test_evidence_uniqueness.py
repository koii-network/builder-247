import pytest
from sqlmodel import SQLModel, create_engine, Session, select
from prometheus_swarm.database.models import Evidence
from pydantic import ValidationError

def create_test_engine():
    """Create an in-memory SQLite engine for testing."""
    # Using SQLite in-memory database for testing
    return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

def test_evidence_uniqueness():
    """
    Integration test to verify evidence uniqueness across the system.
    
    This test ensures that:
    1. Duplicate evidence with same type cannot be inserted
    2. Each evidence entry has a unique identifier
    3. Constraints prevent duplicate evidence submissions
    """
    # Create test engine and tables
    engine = create_test_engine()
    SQLModel.metadata.create_all(engine)
    
    def create_evidence(session: Session, content: str, type: str) -> Evidence:
        """Helper function to create evidence entries"""
        evidence = Evidence(content=content, type=type)
        session.add(evidence)
        session.commit()
        return evidence

    with Session(engine) as session:
        # First evidence submission should succeed
        evidence1 = create_evidence(session, "Test Content 1", "test_type")
        assert evidence1.id is not None
        
        # Attempt to insert identical evidence should fail
        with pytest.raises(Exception) as excinfo:
            create_evidence(session, "Test Content 1", "test_type")
        
        assert "UNIQUE constraint" in str(excinfo.value)

def test_evidence_multiple_types():
    """
    Test that different types of evidence can have the same content
    """
    engine = create_test_engine()
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Create evidence with same content, different types
        evidence1 = Evidence(content="Shared Content", type="type1")
        evidence2 = Evidence(content="Shared Content", type="type2")
        
        session.add(evidence1)
        session.add(evidence2)
        session.commit()
        
        # Verify both evidences were saved
        saved_evidences = session.exec(select(Evidence).where(Evidence.content == "Shared Content")).all()
        assert len(saved_evidences) == 2
        assert {e.type for e in saved_evidences} == {"type1", "type2"}

def test_evidence_content_validation():
    """
    Test validation of evidence content
    """
    # Test empty content
    with pytest.raises(ValidationError) as excinfo:
        Evidence(content="", type="test_type")
    assert "Content cannot be empty or just whitespace" in str(excinfo.value)
    
    # Whitespace-only content
    with pytest.raises(ValidationError) as excinfo:
        Evidence(content="   ", type="test_type")
    assert "Content cannot be empty or just whitespace" in str(excinfo.value)
    
    # Test very long content
    long_content = "a" * 10001  # Exceeding max length
    with pytest.raises(ValidationError) as excinfo:
        Evidence(content=long_content, type="test_type")
    
    # Validate content cannot be completely empty or too long
    assert "String must have at most" in str(excinfo.value)