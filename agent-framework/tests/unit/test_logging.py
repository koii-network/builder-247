"""
Test suite for logging configuration.
"""

import io
import sys
import logging
import pytest
from prometheus_swarm.utils.logging import configure_logging, log_with_context, log_structured_event

def test_configure_logging_default():
    """Test default logging configuration."""
    logger = configure_logging()
    
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO

def test_configure_logging_debug_level():
    """Test debug level logging."""
    logger = configure_logging(log_level="DEBUG")
    
    assert logger.level == logging.DEBUG

def test_logging_with_context():
    """Test adding context to logger."""
    logger = configure_logging()
    context_logger = log_with_context(logger, {"request_id": "123", "user": "test"})
    
    assert isinstance(context_logger, logging.Logger)

def test_log_structured_event(caplog):
    """Test logging a structured event."""
    caplog.set_level(logging.INFO)
    
    log_structured_event(
        "user_login", 
        {"user_id": "123", "method": "email"}, 
        level="INFO"
    )
    
    assert len(caplog.records) > 0
    assert "user_login" in caplog.text
    assert "user_id" in caplog.text
    assert "123" in caplog.text