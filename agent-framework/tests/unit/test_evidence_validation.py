"""
Unit tests for evidence uniqueness validation.
"""

import pytest
from prometheus_swarm.utils.evidence_validation import (
    validate_evidence_uniqueness,
    EvidenceValidationError,
    _are_evidences_similar
)


def test_validate_evidence_uniqueness_with_empty_submissions():
    """Test that a new submission is validated when no existing submissions exist."""
    new_submission = {'evidence': 'Unique task solution'}
    existing_submissions = []

    assert validate_evidence_uniqueness(existing_submissions, new_submission) is True


def test_validate_evidence_uniqueness_with_different_evidence():
    """Test that uniquely different evidence passes validation."""
    existing_submissions = [
        {'evidence': 'First task solution'},
        {'evidence': 'Another task solution'}
    ]
    new_submission = {'evidence': 'Completely different solution'}

    assert validate_evidence_uniqueness(existing_submissions, new_submission) is True


def test_validate_evidence_uniqueness_with_duplicate_evidence():
    """Test that duplicate evidence fails validation."""
    existing_submissions = [
        {'evidence': 'Duplicate task solution'}
    ]
    new_submission = {'evidence': 'Duplicate task solution'}

    with pytest.raises(EvidenceValidationError, match="Evidence is not unique"):
        validate_evidence_uniqueness(existing_submissions, new_submission)


def test_validate_evidence_uniqueness_without_evidence():
    """Test that submissions without evidence are rejected."""
    existing_submissions = []
    new_submission = {}  # No evidence

    with pytest.raises(EvidenceValidationError, match="No evidence provided"):
        validate_evidence_uniqueness(existing_submissions, new_submission)


def test_are_evidences_similar_with_strings():
    """Test string evidence similarity."""
    assert _are_evidences_similar("Hello", "hello") is True
    assert _are_evidences_similar("Hello ", " Hello") is True
    assert _are_evidences_similar("Different", "Text") is False


def test_are_evidences_similar_with_dicts():
    """Test dictionary evidence similarity."""
    evidence1 = {'name': 'Task', 'description': 'Solution'}
    evidence2 = {'name': 'Task', 'description': 'Solution'}
    evidence3 = {'name': 'Different', 'description': 'Other'}

    assert _are_evidences_similar(evidence1, evidence2) is True
    assert _are_evidences_similar(evidence1, evidence3) is False


def test_are_evidences_similar_with_mixed_types():
    """Test similarity with different types."""
    assert _are_evidences_similar(42, 42) is True
    assert _are_evidences_similar(42, 43) is False