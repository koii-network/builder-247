import pytest
import logging
from prometheus_swarm.utils.duplicate_evidence import detect_duplicate_evidence, DuplicateEvidenceError

def test_no_duplicate_evidence():
    """Test that no duplicate evidence passes without issues."""
    evidence_list = [
        {'id': 1, 'data': 'first entry'},
        {'id': 2, 'data': 'second entry'}
    ]
    result = detect_duplicate_evidence(evidence_list)
    assert len(result) == 2

def test_duplicate_evidence_raises_error():
    """Test that duplicate evidence raises an error."""
    evidence_list = [
        {'id': 1, 'data': 'first entry'},
        {'id': 1, 'data': 'duplicate entry'}
    ]
    with pytest.raises(DuplicateEvidenceError):
        detect_duplicate_evidence(evidence_list)

def test_handles_missing_identifier():
    """Test handling of evidence without an identifier."""
    evidence_list = [
        {'id': 1, 'data': 'first entry'},
        {'data': 'entry without id'}
    ]
    result = detect_duplicate_evidence(evidence_list)
    assert len(result) == 2

def test_custom_identifier_key():
    """Test using a custom identifier key."""
    evidence_list = [
        {'custom_id': 'A', 'data': 'first entry'},
        {'custom_id': 'B', 'data': 'second entry'},
        {'custom_id': 'A', 'data': 'duplicate entry'}
    ]
    with pytest.raises(DuplicateEvidenceError):
        detect_duplicate_evidence(evidence_list, identifier_key='custom_id')

def test_logging_duplicate_evidence(caplog):
    """Test that duplicate evidence is logged."""
    caplog.set_level(logging.WARNING)
    
    evidence_list = [
        {'id': 1, 'data': 'first entry'},
        {'id': 1, 'data': 'duplicate entry'}
    ]
    
    with pytest.raises(DuplicateEvidenceError):
        detect_duplicate_evidence(evidence_list)
    
    assert "Duplicate evidence detected" in caplog.text