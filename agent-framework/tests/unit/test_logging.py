"""
Test suite for logging configuration.
"""

import json
import io
import sys
import logging
import structlog
import pytest
from prometheus_swarm.utils.logging import configure_logging, log_with_context

def test_configure_logging_default():
    """Test default logging configuration."""
    logger = configure_logging()
    
    assert isinstance(logger, structlog.BoundLogger)
    assert logger._logger.level == logging.INFO

def test_configure_logging_debug_level():
    """Test debug level logging."""
    logger = configure_logging(log_level="DEBUG")
    
    assert logger._logger.level == logging.DEBUG

def test_logging_with_context():
    """Test adding context to logger."""
    logger = configure_logging()
    context_logger = log_with_context(logger, {"request_id": "123", "user": "test"})
    
    assert context_logger._context == {"request_id": "123", "user": "test"}

def test_configure_logging_json():
    """Test JSON log formatting."""
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    logger = configure_logging(use_json=True)
    logger.info("Test log message", extra_field="value")
    
    # Reset stdout
    sys.stdout = sys.__stdout__
    
    # Parse captured JSON log
    log_output = captured_output.getvalue().strip()
    log_data = json.loads(log_output)
    
    assert "timestamp" in log_data
    assert log_data["event"] == "Test log message"
    assert log_data["extra_field"] == "value"