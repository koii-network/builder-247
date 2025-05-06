import pytest
from unittest.mock import patch, MagicMock
from prometheus_swarm.database.evidence_validation import validate_evidence_uniqueness

def test_validate_evidence_uniqueness_valid():
    # Mock an empty database, so evidence should be unique
    with patch('prometheus_swarm.database.evidence_validation.get_db') as mock_db:
        mock_db_session = MagicMock()
        mock_db.return_value = mock_db_session
        mock_db_session.execute.return_value.scalar.return_value = 0

        evidence = {
            'hash': 'unique_hash',
            'source': 'test_source',
            'type': 'test_type',
            'additional_data': 'some_info'
        }
        
        assert validate_evidence_uniqueness(evidence) is True

def test_validate_evidence_uniqueness_duplicate():
    # Mock a database with existing evidence
    with patch('prometheus_swarm.database.evidence_validation.get_db') as mock_db:
        mock_db_session = MagicMock()
        mock_db.return_value = mock_db_session
        mock_db_session.execute.return_value.scalar.return_value = 1

        evidence = {
            'hash': 'duplicate_hash',
            'source': 'test_source',
            'type': 'test_type'
        }
        
        assert validate_evidence_uniqueness(evidence) is False

def test_validate_evidence_uniqueness_missing_fields():
    # Test missing unique fields
    with pytest.raises(ValueError, match="Missing required unique field"):
        validate_evidence_uniqueness({
            'hash': 'some_hash',
            'source': 'test_source'
        })

def test_validate_evidence_uniqueness_empty_evidence():
    # Test empty evidence
    with pytest.raises(ValueError, match="Evidence cannot be empty"):
        validate_evidence_uniqueness({})

def test_validate_evidence_uniqueness_database_error():
    # Test database connection error
    with patch('prometheus_swarm.database.evidence_validation.get_db') as mock_db:
        mock_db.side_effect = Exception("Database connection failed")
        
        evidence = {
            'hash': 'test_hash',
            'source': 'test_source',
            'type': 'test_type'
        }
        
        with pytest.raises(ValueError, match="Error validating evidence uniqueness"):
            validate_evidence_uniqueness(evidence)