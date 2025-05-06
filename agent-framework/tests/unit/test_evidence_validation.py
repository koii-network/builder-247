import pytest
from prometheus_swarm.database.evidence_validation import validate_evidence_uniqueness
from unittest.mock import patch, MagicMock

def test_validate_evidence_uniqueness_valid():
    # Mock an empty database, so evidence should be unique
    with patch('prometheus_swarm.database.evidence_validation.get_database_connection') as mock_db:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)
        mock_db.return_value.cursor.return_value = mock_cursor

        evidence = {
            'hash': 'unique_hash',
            'source': 'test_source',
            'type': 'test_type',
            'additional_data': 'some_info'
        }
        
        assert validate_evidence_uniqueness(evidence) is True

def test_validate_evidence_uniqueness_duplicate():
    # Mock a database with existing evidence
    with patch('prometheus_swarm.database.evidence_validation.get_database_connection') as mock_db:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_db.return_value.cursor.return_value = mock_cursor

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
    with patch('prometheus_swarm.database.evidence_validation.get_database_connection') as mock_db:
        mock_db.side_effect = Exception("Database connection failed")
        
        evidence = {
            'hash': 'test_hash',
            'source': 'test_source',
            'type': 'test_type'
        }
        
        with pytest.raises(ValueError, match="Error validating evidence uniqueness"):
            validate_evidence_uniqueness(evidence)