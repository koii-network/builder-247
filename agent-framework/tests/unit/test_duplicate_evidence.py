import pytest
import logging
from typing import List, Dict
from prometheus_swarm.utils.duplicate_evidence import (
    validate_unique_evidence, 
    DuplicateEvidenceError, 
    log_evidence_summary,
    filter_duplicates
)

def test_validate_unique_evidence_no_duplicates():
    """Test validation of unique evidence passes."""
    evidence = [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'},
        {'id': 3, 'data': 'third'}
    ]
    
    try:
        validate_unique_evidence(evidence)
    except DuplicateEvidenceError:
        pytest.fail("Unexpected DuplicateEvidenceError raised")

def test_validate_unique_evidence_with_duplicates():
    """Test validation raises error for duplicate evidence."""
    evidence = [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'},
        {'id': 1, 'data': 'duplicate'}
    ]
    
    with pytest.raises(DuplicateEvidenceError, match="Duplicate evidence detected"):
        validate_unique_evidence(evidence)

def test_validate_unique_evidence_missing_key():
    """Test behavior with evidence missing unique key."""
    evidence = [
        {'id': 1, 'data': 'first'},
        {'data': 'no id'},
        {'id': 2, 'data': 'second'}
    ]
    
    # Should not raise an error, just log a warning
    validate_unique_evidence(evidence)

def test_log_evidence_summary(caplog):
    """Test logging of evidence summary."""
    evidence = [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'}
    ]
    
    with caplog.at_level(logging.INFO):
        log_evidence_summary(evidence)
        
    assert "Total evidence entries: 2" in caplog.text

def test_filter_duplicates_first_occurrence():
    """Test filtering duplicates, keeping first occurrence."""
    evidence = [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'},
        {'id': 1, 'data': 'duplicate'}
    ]
    
    filtered = filter_duplicates(evidence)
    
    assert len(filtered) == 2
    assert filtered == [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'}
    ]

def test_filter_duplicates_last_occurrence():
    """Test filtering duplicates, keeping last occurrence."""
    evidence = [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'},
        {'id': 1, 'data': 'duplicate'}
    ]
    
    filtered = filter_duplicates(evidence, keep='last')
    
    assert len(filtered) == 2
    assert filtered == [
        {'id': 2, 'data': 'second'},
        {'id': 1, 'data': 'duplicate'}
    ]

def test_filter_duplicates_invalid_keep_strategy():
    """Test that an invalid keep strategy raises an error."""
    evidence = [
        {'id': 1, 'data': 'first'},
        {'id': 2, 'data': 'second'}
    ]
    
    with pytest.raises(ValueError, match="'keep' must be either 'first' or 'last'"):
        filter_duplicates(evidence, keep='invalid')

def test_filter_duplicates_missing_key():
    """Test filtering duplicates with entries missing unique key."""
    evidence = [
        {'id': 1, 'data': 'first'},
        {'data': 'no id'},
        {'id': 1, 'data': 'duplicate'}
    ]
    
    filtered = filter_duplicates(evidence)
    
    assert len(filtered) == 2
    assert filtered == [
        {'id': 1, 'data': 'first'}
    ]