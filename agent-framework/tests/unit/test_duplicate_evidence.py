import pytest
import logging
from prometheus_swarm.utils.duplicate_evidence import (
    DuplicateEvidenceError, 
    check_duplicate_evidence, 
    log_duplicate_evidence
)

def test_duplicate_evidence_error():
    """Test the DuplicateEvidenceError is raised correctly."""
    existing_evidence = [
        {'id': 1, 'name': 'Evidence 1'},
        {'id': 2, 'name': 'Evidence 2'}
    ]
    new_evidence = {'id': 1, 'name': 'Duplicate Evidence'}

    with pytest.raises(DuplicateEvidenceError) as exc_info:
        check_duplicate_evidence(new_evidence, existing_evidence)
    
    assert str(exc_info.value) == "Evidence with id '1' already exists"
    assert len(exc_info.value.existing_evidence) == 1

def test_no_duplicate_evidence():
    """Test that no error is raised when no duplicates exist."""
    existing_evidence = [
        {'id': 1, 'name': 'Evidence 1'},
        {'id': 2, 'name': 'Evidence 2'}
    ]
    new_evidence = {'id': 3, 'name': 'New Evidence'}

    try:
        check_duplicate_evidence(new_evidence, existing_evidence)
    except DuplicateEvidenceError:
        pytest.fail("Unexpected DuplicateEvidenceError raised")

def test_log_duplicate_evidence(caplog):
    """Test logging of duplicate evidence."""
    caplog.set_level(logging.WARNING)
    
    existing_evidence = [
        {'id': 1, 'name': 'Evidence 1'},
        {'id': 2, 'name': 'Evidence 2'}
    ]
    new_evidence = {'id': 1, 'name': 'Duplicate Evidence'}

    with pytest.raises(DuplicateEvidenceError):
        check_duplicate_evidence(new_evidence, existing_evidence)
    
    assert len(caplog.records) == 1
    log_record = caplog.records[0]
    
    assert log_record.levelname == 'WARNING'
    assert 'Duplicate evidence detected' in log_record.msg
    assert log_record.extra['current_evidence'] == new_evidence
    assert log_record.extra['existing_entries_count'] == 1
    assert log_record.extra['existing_entries_ids'] == [1]

def test_custom_unique_key():
    """Test duplicate checking with a custom unique key."""
    existing_evidence = [
        {'key': 'abc', 'name': 'Evidence 1'},
        {'key': 'def', 'name': 'Evidence 2'}
    ]
    new_evidence = {'key': 'abc', 'name': 'Duplicate Evidence'}

    with pytest.raises(DuplicateEvidenceError) as exc_info:
        check_duplicate_evidence(new_evidence, existing_evidence, unique_key='key')
    
    assert str(exc_info.value) == "Evidence with key 'abc' already exists"