import pytest
import logging
from prometheus_swarm.utils.duplicate_evidence import (
    check_duplicate_evidence, 
    DuplicateEvidenceError, 
    log_duplicate_evidence
)

def test_check_duplicate_evidence_no_duplicates():
    """Test checking evidence with no duplicates."""
    evidence_list = [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'},
        {'id': 3, 'data': 'third'}
    ]
    result = check_duplicate_evidence(evidence_list)
    assert len(result) == 3

def test_check_duplicate_evidence_with_duplicates():
    """Test checking evidence with duplicates."""
    evidence_list = [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'},
        {'id': 1, 'data': 'duplicate'}
    ]
    with pytest.raises(DuplicateEvidenceError):
        check_duplicate_evidence(evidence_list)

def test_check_duplicate_evidence_custom_unique_key():
    """Test checking evidence with a custom unique key."""
    evidence_list = [
        {'uuid': 'a1', 'data': 'first'},
        {'uuid': 'b2', 'data': 'second'},
        {'uuid': 'a1', 'data': 'duplicate'}
    ]
    with pytest.raises(DuplicateEvidenceError):
        check_duplicate_evidence(evidence_list, unique_key='uuid')

def test_check_duplicate_evidence_missing_key():
    """Test handling evidence with missing unique key."""
    evidence_list = [
        {'id': 1, 'data': 'first'},
        {'data': 'no id'},
        {'id': 2, 'data': 'second'}
    ]
    result = check_duplicate_evidence(evidence_list)
    assert len(result) == 3

def test_log_duplicate_evidence(caplog):
    """Test logging of duplicate evidence."""
    caplog.set_level(logging.WARNING)
    duplicate_entries = [
        {'id': 1, 'data': 'duplicate 1'},
        {'id': 2, 'data': 'duplicate 2'}
    ]
    
    log_duplicate_evidence(duplicate_entries)
    
    assert len(caplog.records) == 2
    assert all('Duplicate Evidence' in record.message for record in caplog.records)
    assert all(record.levelno == logging.WARNING for record in caplog.records)

def test_log_duplicate_evidence_custom_log_level(caplog):
    """Test logging of duplicate evidence with custom log level."""
    caplog.set_level(logging.ERROR)
    duplicate_entries = [
        {'id': 1, 'data': 'duplicate 1'}
    ]
    
    log_duplicate_evidence(duplicate_entries, log_level=logging.ERROR)
    
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.ERROR
    assert 'Duplicate Evidence' in caplog.records[0].message