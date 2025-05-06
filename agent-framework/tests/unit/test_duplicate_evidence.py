import pytest
import logging
from prometheus_swarm.utils.duplicate_evidence import (
    detect_duplicate_evidence, 
    log_duplicate_evidence, 
    DuplicateEvidenceError
)

def test_detect_no_duplicates():
    evidence = [
        {"id": 1, "name": "Item1"},
        {"id": 2, "name": "Item2"}
    ]
    result = detect_duplicate_evidence(evidence)
    assert len(result) == 2

def test_detect_duplicates_with_custom_keys():
    evidence = [
        {"id": 1, "name": "Item1", "extra": "data1"},
        {"id": 1, "name": "Item1", "extra": "data2"}
    ]
    result = detect_duplicate_evidence(evidence, unique_keys=["id", "name"])
    assert len(result) == 1

def test_detect_duplicates_raises_error():
    evidence = [
        {"id": 1, "name": "Item1"},
        {"id": 1, "name": "Item1"}
    ]
    with pytest.raises(DuplicateEvidenceError):
        detect_duplicate_evidence(evidence)

def test_detect_empty_list():
    result = detect_duplicate_evidence([])
    assert len(result) == 0

def test_log_duplicate_evidence(caplog):
    caplog.set_level(logging.WARNING)
    evidence = [
        {"id": 1, "name": "Item1"},
        {"id": 1, "name": "Item1"}
    ]
    
    log_duplicate_evidence(evidence)
    
    assert "Total duplicate evidence found: 1" in caplog.text
    assert "Duplicate Evidence:" in caplog.text

def test_duplicate_evidence_complex_object():
    evidence = [
        {"id": 1, "details": {"type": "A", "value": 10}},
        {"id": 1, "details": {"type": "A", "value": 10}}
    ]
    
    with pytest.raises(DuplicateEvidenceError):
        detect_duplicate_evidence(evidence)

def test_custom_unique_key_matching():
    evidence = [
        {"id": 1, "category": "alpha", "value": 100},
        {"id": 2, "category": "alpha", "value": 200},
        {"id": 3, "category": "beta", "value": 300}
    ]
    
    result = detect_duplicate_evidence(evidence, unique_keys=["category"])
    assert len(result) == 1  # Only one item per category