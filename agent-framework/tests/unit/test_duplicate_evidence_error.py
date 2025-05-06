import logging
import pytest
from prometheus_swarm.utils.errors import DuplicateEvidenceError, log_duplicate_evidence

def test_duplicate_evidence_error():
    """Test the DuplicateEvidenceError exception."""
    evidence = {
        'id': '123',
        'name': 'Test Evidence',
        'type': 'document'
    }
    
    with pytest.raises(DuplicateEvidenceError) as exc_info:
        raise DuplicateEvidenceError("Duplicate evidence found", evidence)
    
    assert str(exc_info.value) == "Duplicate evidence found"
    assert exc_info.value.evidence == evidence

def test_log_duplicate_evidence(caplog):
    """Test logging of duplicate evidence."""
    caplog.set_level(logging.WARNING)
    
    evidence = {
        'id': '456',
        'name': 'Another Test Evidence',
        'type': 'record'
    }
    
    log_duplicate_evidence(evidence)
    
    assert len(caplog.records) == 1
    log_record = caplog.records[0]
    
    assert log_record.levelno == logging.WARNING
    assert 'Duplicate evidence detected' in log_record.getMessage()
    assert log_record.extra['evidence'] == evidence