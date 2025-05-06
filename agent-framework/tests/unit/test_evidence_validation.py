"""
Unit tests for evidence uniqueness validation.
"""

import pytest
from prometheus_swarm.utils.evidence_validation import (
    generate_evidence_hash,
    validate_evidence_uniqueness,
    filter_unique_evidences,
    EvidenceValidationError
)


def test_generate_evidence_hash():
    """Test generating a consistent hash for evidence."""
    evidence1 = {"key1": "value1", "key2": 42}
    evidence2 = {"key2": 42, "key1": "value1"}
    
    # Same content should generate the same hash
    assert generate_evidence_hash(evidence1) == generate_evidence_hash(evidence2)
    
    # Different content should generate different hashes
    evidence3 = {"key1": "different"}
    assert generate_evidence_hash(evidence1) != generate_evidence_hash(evidence3)


def test_validate_evidence_uniqueness():
    """Test validating evidence uniqueness."""
    existing_evidences = [
        {"id": 1, "data": "first evidence"},
        {"id": 2, "data": "second evidence"}
    ]
    
    # Unique evidence should pass validation
    unique_evidence = {"id": 3, "data": "third evidence"}
    assert validate_evidence_uniqueness(unique_evidence, existing_evidences) is True
    
    # Duplicate evidence should fail validation
    duplicate_evidence = {"id": 1, "data": "first evidence"}
    assert validate_evidence_uniqueness(duplicate_evidence, existing_evidences) is False


def test_validate_evidence_uniqueness_edge_cases():
    """Test edge cases for evidence uniqueness validation."""
    # Empty list of existing evidences
    unique_evidence = {"id": 1, "data": "test"}
    assert validate_evidence_uniqueness(unique_evidence, []) is True
    
    # Invalid input types
    with pytest.raises(EvidenceValidationError):
        validate_evidence_uniqueness("not a dict", [])
    
    with pytest.raises(EvidenceValidationError):
        validate_evidence_uniqueness({}, "not a list")


def test_filter_unique_evidences():
    """Test filtering unique evidences."""
    existing_evidences = [
        {"id": 1, "data": "first"},
        {"id": 2, "data": "second"}
    ]
    
    new_evidences = [
        {"id": 1, "data": "first"},  # Duplicate
        {"id": 3, "data": "third"},  # Unique
        {"id": 4, "data": "fourth"}  # Unique
    ]
    
    filtered_evidences = filter_unique_evidences(new_evidences, existing_evidences)
    
    # Should only return uniquely new evidences
    assert len(filtered_evidences) == 2
    assert {"id": 3, "data": "third"} in filtered_evidences
    assert {"id": 4, "data": "fourth"} in filtered_evidences


def test_filter_unique_evidences_error_handling():
    """Test error handling in evidence filtering."""
    # Invalid input types
    with pytest.raises(EvidenceValidationError):
        filter_unique_evidences("not a list", [])
    
    # Handling of invalid evidences
    invalid_evidences = [
        {"id": 1},
        "not a dict"
    ]
    assert len(filter_unique_evidences(invalid_evidences, [])) == 1