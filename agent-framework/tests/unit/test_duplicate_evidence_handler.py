import pytest
import logging
from prometheus_swarm.utils.duplicate_evidence_handler import (
    DuplicateEvidenceHandler, 
    DuplicateEvidenceError
)

def test_no_duplicates():
    """Test scenario with no duplicate evidence."""
    handler = DuplicateEvidenceHandler()
    evidence_list = [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'}
    ]
    
    duplicates = handler.check_duplicates(evidence_list)
    assert len(duplicates) == 0

def test_with_duplicates():
    """Test scenario with duplicate evidence."""
    handler = DuplicateEvidenceHandler()
    evidence_list = [
        {'id': 1, 'data': 'first'},
        {'id': 1, 'data': 'duplicate'},
        {'id': 2, 'data': 'third'}
    ]
    
    duplicates = handler.check_duplicates(evidence_list)
    assert len(duplicates) == 1
    assert duplicates[0]['id'] == 1

def test_raise_on_duplicate():
    """Test raising an exception on duplicate evidence."""
    handler = DuplicateEvidenceHandler(raise_on_duplicate=True)
    evidence_list = [
        {'id': 1, 'data': 'first'},
        {'id': 1, 'data': 'duplicate'}
    ]
    
    with pytest.raises(DuplicateEvidenceError):
        handler.check_duplicates(evidence_list)

def test_remove_duplicates():
    """Test removing duplicate evidence."""
    handler = DuplicateEvidenceHandler()
    evidence_list = [
        {'id': 1, 'data': 'first'},
        {'id': 1, 'data': 'duplicate'},
        {'id': 2, 'data': 'third'},
        {'id': 2, 'data': 'another duplicate'}
    ]
    
    unique_evidence = handler.remove_duplicates(evidence_list)
    assert len(unique_evidence) == 2
    unique_ids = [item['id'] for item in unique_evidence]
    assert unique_ids == [1, 2]

def test_custom_identifier_key():
    """Test using a custom identifier key."""
    handler = DuplicateEvidenceHandler()
    evidence_list = [
        {'uuid': 'abc', 'data': 'first'},
        {'uuid': 'abc', 'data': 'duplicate'},
        {'uuid': 'def', 'data': 'third'}
    ]
    
    duplicates = handler.check_duplicates(evidence_list, identifier_key='uuid')
    assert len(duplicates) == 1
    assert duplicates[0]['uuid'] == 'abc'

def test_evidence_without_identifier():
    """Test handling evidence without an identifier."""
    handler = DuplicateEvidenceHandler()
    evidence_list = [
        {'id': 1, 'data': 'first'},
        {'data': 'no id'},
        {'id': 1, 'data': 'duplicate'}
    ]
    
    duplicates = handler.check_duplicates(evidence_list)
    assert len(duplicates) == 1  # Only counts duplicates with valid identifiers