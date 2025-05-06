"""Unit tests for evidence logging and error handling."""

import logging
import pytest
from unittest.mock import patch

from prometheus_swarm.utils.logging import (
    setup_logger, 
    log_duplicate_evidence, 
    handle_evidence_logging
)
from prometheus_swarm.utils.errors import DuplicateEvidenceError

def test_setup_logger():
    """Test logger setup functionality."""
    logger = setup_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0

def test_log_duplicate_evidence_with_id():
    """Test logging of duplicate evidence with an ID."""
    with pytest.raises(DuplicateEvidenceError) as exc_info:
        log_duplicate_evidence(evidence_id='test_evidence_123')
    
    assert 'test_evidence_123' in str(exc_info.value)
    assert isinstance(exc_info.value, DuplicateEvidenceError)

def test_log_duplicate_evidence_with_context():
    """Test logging of duplicate evidence with context."""
    with pytest.raises(DuplicateEvidenceError) as exc_info:
        log_duplicate_evidence(
            evidence_id='test_evidence_456', 
            context={'source': 'unit_test', 'type': 'sample'}
        )
    
    assert 'test_evidence_456' in str(exc_info.value)

def test_handle_evidence_logging_decorator():
    """Test the handle_evidence_logging decorator."""
    @handle_evidence_logging
    def process_evidence(evidence_id=None):
        if evidence_id == 'duplicate':
            log_duplicate_evidence(evidence_id='duplicate')
        return True

    # Normal execution
    assert process_evidence() is True

    # Duplicate evidence
    with pytest.raises(DuplicateEvidenceError):
        process_evidence(evidence_id='duplicate')

def test_handle_evidence_logging_unexpected_error():
    """Test error handling for unexpected exceptions."""
    @handle_evidence_logging
    def faulty_evidence_process():
        raise ValueError("Unexpected error")

    with pytest.raises(ValueError):
        faulty_evidence_process()